import numpy as np
import operator
import dill as pickle
import math
from datetime import datetime
import csv
from time import mktime
import os
import errno
import time

TIME_LOG_BASE = 5

def load_data(df_input,parameter):
	use_products=0
	ratings = {} # {user: [(prod, time, rating)]}
	usermap = {}

	if parameter == "kill":
		parameter = "kill_bin"

	if parameter == "headshot":
		parameter = "head_bin"

	if parameter == "damage":
		parameter = "damage_bin"

	if parameter == "kill_per_min":
		parameter = "kpm_bin"

	if parameter == "head_per_kill":
		parameter = "hpk_bin"

	df_input_new=df_input[['title','gametype','time',parameter]]
	df_input_new=df_input_new[df_input_new[parameter] >= 4]

	#print(df_input_new)
	#print("ok")
	df_input_new['time']=df_input_new['time'].astype('int64')//1e9

	rating_res=df_input_new.groupby('title')[['gametype','time',parameter]].apply(lambda x: [tuple(x) for x in x.values]).to_dict()

	df_input_title=df_input[['title']]
	#print(df_input_title)
	user_res = dict(zip(df_input.title, df_input.title))

	ratings=rating_res
	usermap=user_res

	return ratings, usermap

def process_data(ratings, dataname, use_products):
	keyword = 'prod' if use_products else 'user'
	rating_arr = []

	ids = []

	for user in ratings:
		if len(ratings[user]) <= 1: continue
		rating_counts = [0] * 6
		#iat_counts = [0] * S
		cur_ratings = sorted(ratings[user], key=operator.itemgetter(1))


		#time.sleep(10)

		rating_counts[cur_ratings[0][2] ] += 1
		for i in range(1, len(cur_ratings)):
			#time_diff = cur_ratings[i][1] - cur_ratings[i-1][1]
			#iat_bucket = int(math.floor(math.log(1 + time_diff, TIME_LOG_BASE)))
			rating_counts[cur_ratings[i][2] ] += 1
			#iat_counts[iat_bucket] += 1
		rating_arr.append(rating_counts)
		#iat_arr.append(iat_counts)
		ids.append(user)

	rating_arr = np.array(rating_arr)
	#iat_arr = np.array(iat_arr)
	return (rating_arr, ids)

#pic_load_data = pickle.dumps (load_data)
##rating,user = pickle.loads(pic_load_data)(df,para)
