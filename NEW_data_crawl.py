import time
import pandas as pd
# import socket

# s=socket.socket()
# port = 12397 # Reserve a port for your service
# s.bind(('', port)) #Bind to the port

from bs4 import BeautifulSoup as bs

from chicken_dinner.pubgapi import PUBG
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

##SQL function###

options = Options()
options.add_argument(
    "user-data-dir=C:\\Users\\jeong\\AppData\\Local\\Google\\Chrome\\User Data\\")  # Path to your chrome profile
driver = webdriver.Chrome("C:\\Users\\jeong\\Downloads\\chromedriver.exe", chrome_options=options)

#global df
def data_crawl(url):
    driver.get(url)
    time.sleep(4)

    num = 20
    while num < 20:
        print("clicking MORE button")
        # print(text_to_read)
        more_path = "/html/body/div[2]/section/div[3]/div/div[3]/div[3]/div[1]/div/div/div[2]/button"
        more_button = driver.find_element_by_xpath(more_path)
        more_button.click()
        time.sleep(3)
        num += 20

    html = driver.page_source
    soup = bs(html, 'html.parser')

    date_div = [item["data-original-title"] for item in soup.find_all("div", {'class': "matches-item__reload-time"})
                if "data-original-title" in item.attrs]

    playtime_div = [item["data-game-length"] for item in soup.find_all("div", {'class': "matches-item__time-value"})
                    if "data-game-length" in item.attrs]

    gametype_div = soup.find_all("div", {'class': "matches-item__mode"})

    gametype_list=[]

    for div in gametype_div:
        if div.find("i"):
            new_div=div.find("i")
            new_div_item=new_div.text.strip()
            gametype_list.append(new_div_item)
        else:
            #print(div)
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

    num2= len(date_div)
    print(num2)

    x_num_range = range(0, (num2) * step, step2)

    damage_list = []
    kill_list = []
    head_list = []
    assists_list=[]
    DBNO_list=[]
    distance_list=[]
    walk_distance_list=[]
    ride_distance_list=[]
    heals_list=[]
    boost_list=[]
    revive_list=[]

    for x_num in x_num_range:

        #damage_data = el[x_num][0]
        #print(el[x_num])
        damage_data=el[x_num].split('D')[0]
        damage_list.append(damage_data)
        #print("damage: ", damage_data)

        #print(el[x_num+1])
        kill_head_pre_split = el[x_num + 1].split('K')[0]

        new_kill_data=kill_head_pre_split.split()[0]
        #print("kill count: ", new_kill_data)
        kill_list.append(new_kill_data)
        #print("kill: ", kill_data)

        headshot_data = kill_head_pre_split.split()[1].strip('()')
        #print(headshot_data)
        head_list.append(headshot_data)
        #print("headshot: ", headshot_data)
        #print(head_list)

        assists_data = el[x_num + 2].split('A')[0]
        #print(assists_data)
        assists_list.append(assists_data)
        #print("assists: ", assists_data)

        DBNO_data = el[x_num + 3].split('D')[0]
        #print(DBNO_data)
        DBNO_list.append(DBNO_data)
        #print("DBNO: ", DBNO_data)

        distance_data = el[x_num + 4].split('k')[0]
        distance_data = distance_data.strip()
        #print(distance_data)
        distance_list.append(distance_data)
        #print("distance: ", distance_data)

        walk_distance_data = el[x_num + 5].split('k')[0]
        walk_distance_data = walk_distance_data.strip()
        #print(walk_distance_data)
        walk_distance_list.append(walk_distance_data)
        #print("walk: ", walk_distance_data)

        ride_distance_data = el[x_num + 6].split('k')[0]
        ride_distance_data = ride_distance_data.strip()
        #print(ride_distance_data)
        ride_distance_list.append(ride_distance_data)
        #print("ride : ", ride_distance_data)

        heals_data = el[x_num + 7].split('/')[0]
        heals_data=heals_data.strip()
        #print(heals_data)
        heals_list.append(heals_data)
        #print("heals: ", heals_data)

        boost_data_pre = el[x_num + 7].split('/')[1]
        #print(boost_data_pre)
        boost_data_pre2 = boost_data_pre.split('H')[0]
        #print(boost_data_pre2)
        boost_data=boost_data_pre2.strip()
        #print(boost_data_pre2)
        boost_list.append(boost_data)
        #print("boost: ", boost_data)

        revive_data = el[x_num + 8].split('R')[0]
        #print(revive_data)
        revive_list.append(revive_data)
        #print("revive: ", revive_data)

    # df = pd.DataFrame(columns=['date', 'gametype', 'headshot', 'playtime', 'title', 'kill', 'damage', 'distance', 'DBNO', 'Assists'])

    #df.append({'date':date_div, 'gametype':gametype_div, 'headshot':headshot_data, 'playtime':playtime_div}, ignore_index=True)

    dict1={'playdate':date_div, 'gametype':gametype_list, "headshot": head_list, "playtime": playtime_div, "title":title_soup,"kill":kill_list,
           "damage":damage_list,"distance":distance_list,"walking_distance":walk_distance_list,"ride_distance":ride_distance_list,"DBNO":DBNO_list,"assists":assists_list,
           "heal":head_list,"boost":boost_list,"revive":revive_list
           }
    #df=pd.DataFrame(date_div,columns=["Date"])

    df=pd.DataFrame(dict1)
    return df

    #driver.quit()
    print(df)
    #df.to_csv(r'C:\Users\jeong\Downloads\export_dataframe.csv', index=False, header=True)


#######################
### Non-function part ##
#######################

api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJjMzRmYTQ0MC04NzUwLTAxMzgtMmY3Yy00ZDk1MjEyYTg1YmEiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTkxMTM3OTYzLCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6Implb25nbWluMDgxMi1nIn0.jBLZpQfjcEQDs9a7aIPQG7gvun_za_u_6rBCeZNTLbI"

#pubg = PUBG(api_key, "pc-krjp")
pubg = PUBG(api_key, "pc-kakao")

samples = pubg.samples()

match_list = samples.match_ids
#deltee the line below later#
match_list=['5e6e529f-c9d2-49f1-bb8f-b034089fe577']
#print(match_list)

counter = 0
iteration = 0

for i in match_list:
    match = pubg.match(i)
    counter += 1
    iteration += 1

    if counter == 10:
        print("Waiting cycle={0}".format(iteration))
        time.sleep(60)
        counter = 0

    match_participants = match.participants
    # print(match_participants)

    ###for x in range(len(match_participants)):
    column_names = ["date", "gametype", "headshot","playtime","title","kill","damage","distance","walking distance","ride distance","DBNO","Assists","heal","boost","revive"]
    df1=pd.DataFrame(columns = column_names)
    for x in range(0,5):
        participant_id = match_participants[x].name
        # print("Got an x={0} amount of data".format(x*iteration))
        print(participant_id)

        url_new = 'https://pubg.op.gg/user/' + participant_id
        # url_new='https://dak.gg/profile/' + participant_id
        time.sleep(3)
        #print("waited 5 secs")
        print(url_new)

        ###Handling1
        #df=data_crawl(url_new)
        #df1=df1.append(df,ignore_index=True)
        #print(df1)

    ##cheater
    #url_cheat = 'https://pubg.op.gg/user/baby-thor_10'
    #cheat_df=data_crawl(url_cheat)
    #print(cheat_df)

    ##pro
    url_pro='https://pubg.op.gg/user/Ju_won2'
    pro_df = data_crawl(url_pro)

    #df1.to_csv(r'C:\Users\jeong\Downloads\export_dataframe1.csv', index=False, header=True)
    #cheat_df.to_csv(r'C:\Users\jeong\Downloads\export_dataframe2.csv', index=False, header=True)
    pro_df.to_csv(r'C:\Users\jeong\Downloads\export_dataframe3.csv', index=False, header=True)
    driver.quit()


