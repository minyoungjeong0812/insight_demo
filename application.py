import pandas as pd
import os

from flask import Flask, request, render_template, url_for, redirect, flash
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from operator import itemgetter

import prac2
import prac

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

server = Flask(__name__)
#DESKTOP
server._static_folder = "/home/minyoung/Documents/insight_week2/static"

#LAPTOP
#server._static_folder = "/home/minyoung/Downloads/insight_week2/static"


# Configure session to use filesystem
server.config["SESSION_PERMANENT"] = False
server.config["SESSION_TYPE"] = "filesystem"
Session(server)

# Set up database
engine = create_engine(
    "postgres://ksfkoirmqqkghq:8843ee1b00e9df0948a10b662918ce11131f75859826aca4fecae08f088fdc8e@ec2-52-207-25-133.compute-1.amazonaws.com:5432/d6k5uvvu11hsqa")
db = scoped_session(sessionmaker(bind=engine))

###NEED TO INPUT RAW DAMAGE, kill data
#df_bin = pd.read_sql_query('select * from "all_users"',con=engine)
df_raw= pd.read_sql_query('select * from "all_users_raw"',con=engine)
available_indicators = ['kill','headshot','kill_per_min','headshot_per_kill','damage','distance','dbno','assists','heal','boost','revive']
######################
dash_app0 = dash.Dash(__name__, server=server, url_base_pathname='/dashboard0/', external_stylesheets=external_stylesheets)
dash_app1 = dash.Dash(__name__, server=server, url_base_pathname='/dashboard1/', external_stylesheets=external_stylesheets)

# dash_app0 : my own
dash_app0.layout = html.Div(children=[
    html.Div(children='''
        UserID to graph:
    '''),
    dcc.Input(id='input', value='Required field', type='text'),

    html.Div([
    dcc.Dropdown(id='yaxis-column',options=[{'label': i.upper(), 'value': i} for i in available_indicators],
                value='kill')], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})

    ,html.Div(id='output-graph'),])

@dash_app0.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value'), Input('yaxis-column', 'value')]
)
def update_value(input_data, parameter):

    df = df_raw[df_raw['title'] == input_data]
    df['kill_per_min'] = 60*df['kill']/df['playtime']
    df['headshot_per_kill'] = df['headshot']/df['kill']

    df.reset_index(inplace=True)
    df.set_index("playdate", inplace=True)
    #df = df.drop("Symbol", axis=1)
    fig = go.Figure(data=go.Scatter(x=df.index,
                                y=df[parameter], mode='markers',marker_color=df[parameter],text=df['gametype']))

    if len(df)==0:
        text_to_show = "Cannot find user data"
    else:
        text_to_show = input_data + " : " + parameter.upper()

    fig.update_layout(
        title={
            'text': text_to_show,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    return dcc.Graph(id='example-graph',figure=fig)

###########################
# dash_app1 : my own again
dash_app1.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

	html.H2('All user data'),

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
    import urllib.parse
    parsed_url = urllib.parse.urlparse(pathname)
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    name = parsed_query['username'][0]

    df = df_raw

    df = df[df['gametype'] != 'Event']
    df['kill_per_min'] = 60*df['kill']/df['playtime']
    df['headshot_per_kill'] = df['headshot']/df['kill']

    #df['gameplay_date']=df['playdate']
    df.reset_index(inplace=True)
    df.set_index("playdate", inplace=True)
    # #df = df.drop("Symbol", axis=1)

    print(df.transpose())
    df2 = df[df['title'] == name]

    import plotly.express as px

    # ##Need to assign correct type (kill, kill per min) per each user##

    ##Fig: only suspicious
    fig = px.histogram(df2, x=parameter, nbins=10, color="gametype", marginal="rug", hover_data=df2.columns)

    fig3 = go.Figure(data=go.Scatter(x=df2.index,y=df2[parameter],mode='markers'))

    ##Fig2: all users
    fig2 = px.histogram(df, x=parameter, nbins=10, color="gametype", marginal="box", hover_data=df.columns)

    return html.Div([html.H3('Player : {}'.format(name))]), dcc.Graph(id='example-graph',figure=fig,style={'width': '100%', 'display':'inline-block'}),\
           dcc.Graph(id='example-graph',figure=fig2), dcc.Graph(id='example-graph',figure=fig3,style={'width': '100%', 'display':'inline-block'})

####FLASK####
@server.route('/')
def home():
    return render_template("home.html", message="WORKING")

@server.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        f = request.files['file']

        if not f:
            return "No file"

        df_bin = pd.read_sql_query('select * from "all_users"', con=engine)

        df_added = pd.read_csv(f)
        df2 = prac.df_create(df_added)

        if len(df2.merge(df_bin).drop_duplicates())  == len(df2):
            flash("You already have this user's data", 'warning')
            return redirect(url_for('upload_csv'))
        else:
            #got union values in the dataframes#
            df_final = df_bin.merge(df2, how='outer', indicator=False)

            ##getting existing rows
            df_existing = df_bin.merge(df2, indicator=False)

            #getting only unique rows in the newly added csv#
            df_unique=df_bin.merge(df2, how='outer', indicator=True).loc[lambda x : x['_merge'] == 'right_only']

            if len(df_unique) ==0:
                message="All rows already exist in the database"
                return render_template('index.html', unique=len(df_unique), dict=df_existing.to_dict(),
                                       existing=len(df_existing),message=message)
            else:
                message = "Done"
                df_unique=df_unique.drop('_merge',axis=1)
                df_unique.to_sql('all_users', con=engine, index=False, if_exists='append')
                df_added.to_sql('all_users_raw', con=engine, index=False, if_exists='append')
                return render_template('index.html', message=message, unique=len(df_unique), dict=df_unique.to_dict(),existing=len(df2.merge(df_bin)))

    else:
        #return prac2.print_hello("hareen")
        return render_template('submit.html')

@server.route('/analysis',methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        df_bin = pd.read_sql_query('select * from "all_users"', con=engine)

        parameter = request.form.get("parameter")
        print(parameter)

        ratings, usermap = preprocess.load_data(df_bin,parameter)

        name = 'insight_analysis'
        USE_PRODUCTS=0
        USE_TIMES=0

        (rating_arr, iat_arr, ids) = preprocess.process_data(ratings,name,USE_PRODUCTS)
        (rating_arr, iat_arr) = (np.array(rating_arr), np.array(iat_arr))

        ##detect can be pickeld##

        suspn = detect.detect(rating_arr, iat_arr, USE_TIMES, 1)
        susp_sorted = np.array([(x[0]) for x in sorted(enumerate(suspn), key=itemgetter(1), reverse=True)])
        bad = susp_sorted[range(10)]
        bad_rate_ave_5 = np.array([0] * 6, dtype=float)
        bad_time_ave = np.array([0] * iat_arr.shape[1], dtype=float)

        dict5 = {}
        dict1 ={}
        for i in range(len(suspn)):
            cur = (rating_arr[i, :] / np.sum(rating_arr[i, :]))
            if i in bad:
                if cur[0] > cur[5]:
                    key = usermap[ids[i]]
                    value = ratings[key]
                    dict1[key] = value
                else:
                    key = usermap[ids[i]]
                    value = ratings[key]
                    dict5[key] = value

                    bad_rate_ave_5 += cur
                bad_time_ave += (iat_arr[i, :] / np.sum(iat_arr[i, :]))

        bad_rate_ave_5 = bad_rate_ave_5 / np.sum(bad_rate_ave_5)
        bad_time_ave = bad_time_ave / np.sum(bad_time_ave)

        db.execute('TRUNCATE TABLE "bad_user";')
        db.commit()
        print("cleared database")

        bad_user_id = list(dict5.keys())
        bad_df = pd.DataFrame(bad_user_id)
        bad_df = bad_df.rename(columns={0: 'username'})

        bad_df.to_sql('bad_user', con=engine, index=False, if_exists='append')
        bad_user = db.execute("SELECT * from bad_user")

        #print(bad_user.fetchall())

        return render_template('success.html', bad_user=bad_user, message=parameter)
    else:
        return render_template('analysis_input.html')


@server.route("/analysis/<username>", methods=["GET", "POST"])
def search_res(username):
    if request.method == "POST":
        return "ok"
    else:
        return redirect(url_for('/dashboard1/',username=username))


app = DispatcherMiddleware(server, {
    '/mydash': dash_app0.server, '/mydash2': dash_app1.server
})

run_simple('127.0.0.1', 8080, app, use_reloader=True, use_debugger=True)
#if __name__ == '__main__':
    # db.create_all()
    #app.run_server(debug=True)