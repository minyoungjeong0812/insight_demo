#loading neccessary pacakages in
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


def load_data(df_input,parameter):
	#creating empty dictionaries to store user parameter (rating) info and user info
	ratings = {}
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

	#selecting records where their user parameter bins are greater than 4.
	df_input_new=df_input_new[df_input_new[parameter] >= 4]

	df_input_new['time']=df_input_new['time'].astype('int64')//1e9

	#converting user parameter dataframe to dicitonary
	rating_res=df_input_new.groupby('title')[['gametype','time',parameter]].apply(lambda x: [tuple(x) for x in x.values]).to_dict()

	#converting user info dataframe to dictionary
	df_input_title=df_input[['title']]
	user_res = dict(zip(df_input.title, df_input.title))

	ratings=rating_res
	usermap=user_res

	return ratings, usermap

def process_data(ratings, dataname, use_products):

	#creating empty lists for user parameter (rating) and id
	rating_arr = []
	ids = []

	#looping over users
	for user in ratings:
		if len(ratings[user]) <= 1: continue
		# creating list to count occurences of each bin
		rating_counts = [0] * 6

		#sort the ratings dictionary
		cur_ratings = sorted(ratings[user], key=operator.itemgetter(1))

		#add +1 for a specific bin if it existed in the ratings dicitionary
		rating_counts[cur_ratings[0][2] ] += 1

		#looping over each user's rating
		for i in range(1, len(cur_ratings)):
			rating_counts[cur_ratings[i][2] ] += 1

		rating_arr.append(rating_counts)
		ids.append(user)

	rating_arr = np.array(rating_arr)

	return (rating_arr, ids)
