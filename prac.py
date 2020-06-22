import numpy as np
import pandas as pd

def df_create(df):
       df=df[df['gametype']!='Event']

       df.loc[:,'username'] = df['title']

       bins = [-np.inf, 1, 3, 6, 8, 10, np.inf]
       labels = [0,1,2,3,4,5]
       df['kill_bin'] = pd.cut(df['kill'], bins=bins, labels=labels)

       df['kill_per_min'] = 60*df['kill']/df['playtime']

       df['head_per_kill']=df['headshot']/df['kill']

       df1=df.drop(['dbno','assists','heal','boost','revive'],axis=1)

       df1['head_per_kill']=df1['head_per_kill'].fillna(0)


       bins = [-np.inf, 1, 2, 3, 4, 5, np.inf]
       labels = [0,1,2,3,4,5]
       df1['head_bin'] = pd.cut(df1['headshot'], bins=bins, labels=labels)


       bins = [-np.inf, 100, 200, 300, 400, 500, np.inf]
       labels = [0,1,2,3,4,5]
       df1['damage_bin'] = pd.cut(df1['damage'], bins=bins, labels=labels)

       bins = [-np.inf, 0.1, 0.2, 0.4, 0.6 , 0.8, np.inf]
       labels = [0,1,2,3,4,5]
       df1['hpk_bin'] = pd.cut(df1['head_per_kill'], bins=bins, labels=labels)

       bins = [-np.inf, 2, 3, 5, 7 ,9, np.inf]
       labels = [0,1,2,3,4,5]
       df1['dist_bin'] = pd.cut(df1['distance'], bins=bins, labels=labels)

       bins = [-np.inf, 0.1, 0.2, 0.3, 0.4 , 0.5, np.inf]
       labels = [0,1,2,3,4,5]
       df1['kpm_bin'] = pd.cut(df1['kill_per_min'], bins=bins, labels=labels)
       df1['playdate']=pd.to_datetime(df['playdate'], infer_datetime_format=True)

       cols=['gametype','head_bin','title','username','kill_bin','damage_bin','kpm_bin','hpk_bin','dist_bin','playdate']

       df2=df1[cols]

       return df2