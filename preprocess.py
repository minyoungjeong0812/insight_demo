import numpy as np
import operator
import dill as pickle
import math
from datetime import datetime
import csv
from time import mktime
import os
import errno

TIME_LOG_BASE = 5

def load_data(df_input,parameter):
	use_products=0

	ratings = {} # {user: [(prod, time, rating)]}
	usermap = {}

	# note: users are labelled 1 through (num_users) without gaps
	for index, row in df_input.iterrows():
		if parameter == "kill":
			tokkit = int(row['kill_bin'])

		elif parameter == "headshot":
			tokkit = int(row['head_bin'])

		elif parameter == "damage":
			tokkit = int(row['damage_bin'])

		elif parameter == "kill_per_min":
			tokkit = int(row['kpm_bin'])

		elif parameter == "head_per_kill":
			tokkit = int(row['hpk_bin'])

		else:
			tokkit = int(row['dist_bin'])

		user, username, prod, rating, time = [row[3], row[4], row[1], tokkit, str(row[10])]
		#print(parameter)
		#print(tokkit)
		time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
		time = mktime(time.timetuple())

		usermap[user] = username
		if use_products:
			user, prod = prod, user
		if user not in ratings:
			ratings[user] = []
		ratings[user].append((prod, time, rating))

	return ratings, usermap

def process_data(ratings, dataname, use_products):
	keyword = 'prod' if use_products else 'user'
	rating_arr = []
	iat_arr = []
	ids = []
	max_time_diff = -1
	for user in ratings:
		cur_ratings = sorted(ratings[user], key=operator.itemgetter(1))
		#print(cur_ratings)
		for i in range(1, len(cur_ratings)):
			time_diff = cur_ratings[i][1] - cur_ratings[i-1][1]
			max_time_diff = max(max_time_diff, time_diff)

	S = int(1 + math.floor(math.log(1 + max_time_diff, TIME_LOG_BASE)))
	for user in ratings:
		if len(ratings[user]) <= 1: continue
		rating_counts = [0] * 6
		iat_counts = [0] * S
		cur_ratings = sorted(ratings[user], key=operator.itemgetter(1))
		rating_counts[cur_ratings[0][2] ] += 1
		for i in range(1, len(cur_ratings)):
			time_diff = cur_ratings[i][1] - cur_ratings[i-1][1]
			iat_bucket = int(math.floor(math.log(1 + time_diff, TIME_LOG_BASE)))
			rating_counts[cur_ratings[i][2] ] += 1
			iat_counts[iat_bucket] += 1
		rating_arr.append(rating_counts)
		iat_arr.append(iat_counts)
		ids.append(user)

	rating_arr = np.array(rating_arr)
	iat_arr = np.array(iat_arr)
	return (rating_arr, iat_arr, ids)

#pic_load_data = pickle.dumps (load_data)
##rating,user = pickle.loads(pic_load_data)(df,para)

