#loading neccessary packages in
import pandas as pd
import os

from flask import Flask, request, render_template, url_for, redirect, flash
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from operator import itemgetter

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

import plotly.express as px
from plotly.subplots import make_subplots

import preprocess
import detect

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

import werkzeug
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

import numpy as np
import csv
import io
import dash
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#flask server initiation
server = Flask(__name__)

# Configure session to use filesystem
server.config["SESSION_PERMANENT"] = False
server.config["SESSION_TYPE"] = "filesystem"
Session(server)

# Set up database
engine = create_engine(
    "postgres://ksfkoirmqqkghq:8843ee1b00e9df0948a10b662918ce11131f75859826aca4fecae08f088fdc8e@ec2-52-207-25-133.compute-1.amazonaws.com:5432/d6k5uvvu11hsqa")
db = scoped_session(sessionmaker(bind=engine))

#indicator list to create dropdown on dash web app page
available_indicators = ['kill','headshot','kill_per_min','headshot_per_kill','damage']

#dash web app creation
dash_app1 = dash.Dash(__name__, server=server, url_base_pathname='/dashboard1/', external_stylesheets=external_stylesheets)


dash_app1.layout = html.Div([

    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

	html.H2('General user data + Searched player data'),

    html.Div([
    dcc.Dropdown(id='yaxis-column',options=[{'label': i.upper(), 'value': i} for i in available_indicators],
                value='kill')], style={'width': '48%'}),

    dcc.Loading(
        id="loading-1",
        type="default",
        children= html.Div(id='output-graph2')),

    html.Div(id='page-content'),

    dcc.Loading(
        id="loading-2",
        type="default",
        children=html.Div([
        html.Div(id='output-graph', className="six columns"),
        html.Div(id='output-graph3', className="six columns"),
    ], className="row"))
])

@dash_app1.callback([dash.dependencies.Output('page-content', 'children'),Output(component_id='output-graph', component_property='children'),
                     Output(component_id='output-graph2', component_property='children'), Output(component_id='output-graph3', component_property='children')],
              [dash.dependencies.Input('url', 'href'),Input('yaxis-column', 'value')])

def display_page(pathname,parameter):
    #importing url address to parse out the user id only
    import urllib.parse
    parsed_url = urllib.parse.urlparse(pathname)
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    name = parsed_query['username'][0]

    #loading in the data from heroku sql database to pandas dataframe
    df=pd.read_sql_query('select playdate, playtime, title, gametype,kill,headshot,damage from "all_users_raw"',con=engine).drop_duplicates(subset=['playdate', 'gametype', 'headshot', 'playtime'])

    #excluding "event" game type : event game type will result in unusual 30-40 kills in 10 mins even for general users
    df = df[df['gametype'] != 'Event']

    #getting kill_per_min feature (kills per minute)
    df['kill_per_min'] = 60*df['kill']/df['playtime']

    #getting headshot_per_min feature (headshot per minute)
    df['headshot_per_kill'] = df['headshot']/df['kill']

    #converting user id (title) to lower case for easier finding
    df['title2']=df['title'].str.lower()

    #resetting and setting dataframe index to playdate for easier plotting
    df.reset_index(inplace=True)
    df.set_index("playdate", inplace=True)

    #finding the rows in the dataframe that belongs to interested (serached) user and saving it as df2
    df2 = df[df['title2'] == name.lower()]

    ##Figure creation (fig : seperate user data histogram, fig 3: separate time series user data )
    fig = px.histogram(df2, x=parameter, nbins=10, color="gametype", marginal="rug", hover_data=df2.columns)

    fig3 = go.Figure(data=go.Scatter(x=df2.index,y=df2[parameter],mode='markers'))

    #Figure creation (fig2: overlaid general user + selected user histogram data for different game type)
    fig2 = make_subplots(
    rows=4, cols=2,shared_xaxes=False, vertical_spacing=0.1,
    subplot_titles=("Squad", "Duo", "Solo", "Ranked FPP","Solo FPP","Duo FPP","Squad FPP"))

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Squad'][parameter], histnorm='probability',nbinsx=10, marker_color='#707070',opacity=0.9,bingroup=1, name="General user - Squad"),row=1,col=1)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Squad'][parameter], histnorm='probability',nbinsx=10, marker_color='#f00800',opacity=0.9, bingroup=1, name=df2['title'].iloc[0] + " - Squad"),row=1,col=1)

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Duo'][parameter], histnorm='probability',nbinsx=10,bingroup=7,marker_color='#707070',opacity=0.9, name="General user - Duo"),row=1,col=2)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Duo'][parameter], histnorm='probability',nbinsx=10,marker_color='#f00800',opacity=0.9, bingroup=7,name=df2['title'].iloc[0] + " - Duo" ),row=1,col=2)

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Solo'][parameter], histnorm='probability', nbinsx=10, marker_color='#707070',opacity=0.9, bingroup=2, name= "General user - Solo"),row=2,col=1)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Solo'][parameter], histnorm='probability', nbinsx=10, marker_color='#f00800',opacity=0.9, bingroup=2, name=df2['title'].iloc[0] + " - Solo"),row=2,col=1)

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Ranked FPP'][parameter], histnorm='probability', nbinsx=10, marker_color='#707070',opacity=0.9,bingroup=3, name = "General user - Ranked FPP"),row=2,col=2)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Ranked FPP'][parameter], histnorm='probability',nbinsx=10, marker_color='#f00800',opacity=0.9, bingroup=3, name=df2['title'].iloc[0] + " - Ranked FPP"),row=2,col=2)

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Solo FPP'][parameter], histnorm='probability',nbinsx=10, bingroup=4, marker_color='#707070',opacity=0.9, name= "General user - Solo FPP"),row=3,col=1)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Solo FPP'][parameter], histnorm='probability',nbinsx=10, marker_color='#f00800',opacity=0.9, bingroup=4, name=df2['title'].iloc[0] + " - Solo FPP"),row=3,col=1)

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Duo FPP'][parameter], histnorm='probability',nbinsx=10, bingroup=5,marker_color='#707070',opacity=0.9, name= "General user - Duo FPP"),row=3,col=2)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Duo FPP'][parameter], histnorm='probability',nbinsx=10, marker_color='#f00800',opacity=0.9, bingroup=5, name=df2['title'].iloc[0] + " - Duo FPP"),row=3,col=2)

    fig2.append_trace(go.Histogram(x=df[df['gametype']=='Squad FPP'][parameter], histnorm='probability',bingroup=6,marker_color='#707070',opacity=0.9,nbinsx=10, name="General user - Squad FPP"),row=4,col=1)
    fig2.add_trace(go.Histogram(x=df2[df2['gametype']=='Squad FPP'][parameter], histnorm='probability',marker_color='#f00800',opacity=0.9,bingroup=6, nbinsx=10, name=df2['title'].iloc[0] + " - Squad FPP"),row=4,col=1)

    # Update xaxis properties
    fig2.update_xaxes(title_text=parameter.upper(), row=1, col=1)
    fig2.update_xaxes(title_text=parameter.upper(), row=1, col=2)
    fig2.update_xaxes(title_text=parameter.upper(), row=2, col=1)
    fig2.update_xaxes(title_text=parameter.upper(), row=2, col=2)
    fig2.update_xaxes(title_text=parameter.upper(), row=3, col=1)
    fig2.update_xaxes(title_text=parameter.upper(), row=3, col=2)
    fig2.update_xaxes(title_text=parameter.upper(), row=4, col=1)

    # Update yaxis properties
    fig2.update_yaxes(title_text="Probability", row=1, col=1)
    fig2.update_yaxes(title_text="Probability", row=1, col=2)
    fig2.update_yaxes(title_text="Probability", row=2, col=1)
    fig2.update_yaxes(title_text="Probability", row=2, col=2)
    fig2.update_yaxes(title_text="Probability", row=3, col=1)
    fig2.update_yaxes(title_text="Probability", row=3, col=2)
    fig2.update_yaxes(title_text="Probability", row=4, col=1)

    fig2.update_layout(showlegend=False,title_text="Searched user (RED) vs General user (Grey)", autosize=False,width=1500, height=1300, bargap=0.2, bargroupgap=0.3)

    return html.Div([html.H3('Player : {}'.format(df2['title'].iloc[0]))]), dcc.Graph(id='example-graph',figure=fig,style={'width': '100%', 'display':'inline-block'}),\
           dcc.Graph(id='example-graph',figure=fig2), dcc.Graph(id='example-graph',figure=fig3,style={'width': '100%', 'display':'inline-block'})

####FLASK pages####
@server.route('/')
def home():
    return render_template("home.html", message="WORKING")


@server.route("/check", methods=["GET", "POST"])
def check():
    if request.method == 'POST':

        check=request.form.get('check')

        #same as above, getting the data from heroku sql database and saving it as df. Then filtering out the event game type
        df=pd.read_sql_query('select kill,headshot,damage,playtime,title,playdate,gametype from "all_users_raw"',con=engine).drop_duplicates(subset=['playdate', 'gametype', 'headshot', 'playtime'])
        df = df[df['gametype'] != 'Event']

        #creating new features that can be meaningful
        df['kill_per_min'] = 60*df['kill']/df['playtime']
        df['head_per_kill']=df['headshot']/df['kill']
        df['head_per_kill']=df['head_per_kill'].fillna(0)

        #creating bins for user parameters
        bins = [-np.inf, 1, 3, 6, 8, 10, np.inf]
        labels = [0,1,2,3,4,5]
        df['kill_bin'] = pd.cut(df['kill'], bins=bins, labels=labels)

        bins = [-np.inf, 1, 2, 3, 4, 5, np.inf]
        labels = [0,1,2,3,4,5]
        df['head_bin'] = pd.cut(df['headshot'], bins=bins, labels=labels)

        bins = [-np.inf, 100, 200, 300, 400, 500, np.inf]
        labels = [0,1,2,3,4,5]
        df['damage_bin'] = pd.cut(df['damage'], bins=bins, labels=labels)

        bins = [-np.inf, 0.1, 0.2, 0.4, 0.6 , 0.8, np.inf]
        labels = [0,1,2,3,4,5]
        df['hpk_bin'] = pd.cut(df['head_per_kill'], bins=bins, labels=labels)

        bins = [-np.inf, 0.1, 0.2, 0.3, 0.4 , 0.5, np.inf]
        labels = [0,1,2,3,4,5]
        df['kpm_bin'] = pd.cut(df['kill_per_min'], bins=bins, labels=labels)
        df['time']=pd.to_datetime(df['playdate'], infer_datetime_format=True)

        cols=['gametype','head_bin','title','kill_bin','damage_bin','kpm_bin','hpk_bin','time']

        #filtering out for defined columns
        df_bin=df[cols]

        #user parameter list to loop over
        parameter_list = ['kill_bin','head_bin','damage_bin','kpm_bin','hpk_bin']

        #selecting top 1% deviators
        target = int(0.01*df_bin['title'].nunique())

        #creating an empty dataframe to store information later
        df_bad_total = pd.DataFrame(columns=['username','parameter'])

        #looping over definied parameters
        for parameter in parameter_list:
            #ratings : parameter bin, usermap : to store userid information
            #separate preprocess file processes the data to get arrays in a needed shape
            ratings, usermap = preprocess.load_data(df_bin,parameter)

            #arbitrary name
            name = 'insight_analysis'

            #if use_products is 0, we get dicitonary in a format where key is a user title and values are user parameters
            #if use_times is 0, we are not collecting temporal user behaviors. We are not interested in this.
            USE_PRODUCTS=0
            USE_TIMES=0

            (rating_arr, ids) = preprocess.process_data(ratings,name,USE_PRODUCTS)
            (rating_arr) = np.array(rating_arr)

            #feeding in rating_arr to 'detect' function saved in a separate file
            suspn = detect.detect(rating_arr, USE_TIMES, 1)

            #sorting the suspicion parameter
            susp_sorted = np.array([(x[0]) for x in sorted(enumerate(suspn), key=itemgetter(1), reverse=True)])

            #preventing out of range problem
            if target >= len(susp_sorted):
                target=len(susp_sorted)

            #list that contains bad user indices
            bad = susp_sorted[range(target)]

            #empty dicitionary to contain bad user data
            dict5 = {}

            for i in bad:
                key=usermap[ids[i]]
                value=ratings[key]
                dict5[key]=value

            bad_user_id = list(dict5.keys())

            #inserting obtained bad user data back to empty bad user dataframe (df_bad_total) defined above
            bad_df = pd.DataFrame(bad_user_id)
            bad_df = bad_df.rename(columns={0: 'username'})
            bad_df['parameter'] = parameter
            df_bad_total=df_bad_total.append(bad_df)

        #selecting the SQL records that correspond to the serached user title
        check_res2 = db.execute("SELECT * from all_users_raw where lower(title) = :title", {"title": str(check).lower()})

        #check the resultant bad user dataframe's length
        df_len_check=len(df_bad_total[df_bad_total['username'].str.lower() == check.lower()])

        #if statements to create different pages depending on conditions
        if df_len_check == 0 and check_res2.rowcount ==0:
            return render_template("data_load.html",check=check)

        elif df_len_check == 0 and check_res2.rowcount !=0:
            return render_template("check_res2.html",check=check)

        else:
            #codes to create a page if user data was in the original SQL database and bad user dataframe to show what parameters the user is suspicious for
            check_res=df_bad_total[df_bad_total['username'].str.lower() == check.lower()].to_dict()
            user=check_res['username']
            check_res=check_res['parameter']

            mydict2={}
            for x in check_res.values():
                if x=="kill_bin":
                    mydict2.update({"parameter1": "Too much kill"})
                if x == "head_bin":
                    mydict2.update({"parameter2": "Too much headshot"})
                if x == "damage_bin":
                    mydict2.update({"parameter3": "Too much damage"})
                if x == "kpm_bin":
                    mydict2.update({"parameter4": "Too much kills per minute"})
                if x == "hpk_bin":
                    mydict2.update({"parameter5": "Too much headshots per kill"})

            mydict4={}
            if user:
                x=list(user)[0]
                y=user[x]
                mydict4.update({"username":y})

            return render_template("check_res.html",check=check,check_res=mydict2,user=mydict4)

    return render_template("check.html")

#route for loading data section which will be executed when the user data does not exisit in the original user database
@server.route("/data_load",methods=["POST"])
def data_load():
    name= request.form.get("custId")
    print("given name: ", name)

    #getting new user data from pubg.op.gg website to load in to the heroku sql database using beatuifulsoup
    url = 'https://pubg.op.gg/user/'+ name
    req = Request(url)
    webpage = urlopen(req).read()

    soup = bs(webpage,"html.parser")

    date_div = [item["data-ago-date"] for item in soup.find_all("div", {'class': "matches-item__reload-time"})
                if "data-ago-date" in item.attrs]

    playtime_div = [item["data-game-length"] for item in soup.find_all("div", {'class': "matches-item__time-value"})
                    if "data-game-length" in item.attrs]

    gametype_div = soup.find_all("div", {'class': "matches-item__mode"})

    gametype_list = []

    if len(date_div) ==0:
        return render_template("error.html")

    for div in gametype_div:
       if div.find("i"):
          new_div = div.find("i")
          new_div_item = new_div.text.strip()
          gametype_list.append(new_div_item)
       else:
          new_div = div.find("span")
          new_div_item = new_div.text.strip()
          gametype_list.append(new_div_item)

    title_soup = soup.find("div", {'id': "userNickname"}).text.strip()
    print(title_soup)
    el = []
    match_detail_div = soup.find_all("div", {'class': "matches-detail__item-inner"})
    for m in match_detail_div:
       m2 = m.text.replace('\n', '').strip()
       el.append(m2)

    step = 9
    step2 = 9

    num2 = len(date_div)

    x_num_range = range(0, (num2) * step, step2)

    damage_list = []
    kill_list = []
    head_list = []
    assists_list = []
    DBNO_list = []
    distance_list = []
    walk_distance_list = []
    ride_distance_list = []
    heals_list = []
    boost_list = []
    revive_list = []

    for x_num in x_num_range:
       damage_data = el[x_num].split('D')[0]
       damage_list.append(damage_data)

       kill_head_pre_split = el[x_num + 1].split('K')[0]
       new_kill_data = kill_head_pre_split.split()[0]
       kill_list.append(new_kill_data)


       headshot_data = kill_head_pre_split.split()[1].strip('()')
       head_list.append(headshot_data)

       assists_data = el[x_num + 2].split('A')[0]
       assists_list.append(assists_data)

       DBNO_data = el[x_num + 3].split('D')[0]
       DBNO_list.append(DBNO_data)

       distance_data = el[x_num + 4].split('k')[0]
       distance_data = distance_data.strip()
       distance_list.append(distance_data)


       walk_distance_data = el[x_num + 5].split('k')[0]
       walk_distance_data = walk_distance_data.strip()
       walk_distance_list.append(walk_distance_data)


       ride_distance_data = el[x_num + 6].split('k')[0]
       ride_distance_data = ride_distance_data.strip()
       ride_distance_list.append(ride_distance_data)

       heals_data = el[x_num + 7].split('/')[0]
       heals_data = heals_data.strip()
       heals_list.append(heals_data)

       boost_data_pre = el[x_num + 7].split('/')[1]
       boost_data_pre2 = boost_data_pre.split('H')[0]
       boost_data = boost_data_pre2.strip()
       boost_list.append(boost_data)


       revive_data = el[x_num + 8].split('R')[0]
       revive_list.append(revive_data)

    dict1 = {'playdate': date_div, 'gametype': gametype_list, "headshot": head_list, "playtime": playtime_div,
             "title": title_soup, "kill": kill_list,
             "damage": damage_list, "distance": distance_list, "walking_distance": walk_distance_list,
             "ride_distance": ride_distance_list, "dbno": DBNO_list, "assists": assists_list,
             "heal": head_list, "boost": boost_list, "revive": revive_list
             }

    df = pd.DataFrame(dict1)
    df['playdate']=pd.to_datetime(df['playdate'], infer_datetime_format=True)
    df['damage']=df['damage'].replace({',':''},regex=True).apply(pd.to_numeric,1)

    message="DONE"
    df.to_sql('all_users_raw', con=engine, index=False, if_exists='append')

    return render_template("index.html",message=message,unique=len(df))


@server.route("/analysis/<username>", methods=["GET", "POST"])
def search_res(username):
    if request.method == "POST":
        return "ok"
    else:
        return redirect(url_for('/dashboard1/',username=username))

app = DispatcherMiddleware(server, {'/mydash2': dash_app1.server})

if __name__ == '__main__':
    server.run(debug=True)
