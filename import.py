import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://sollsrywssgqwp:3c79a640882fb271f04b87c85e54e09c654059316404be7bcdb671cc6bf7976d@ec2-35-171-31-33.compute-1.amazonaws.com:5432/d77ns8sefglun7")
db = scoped_session(sessionmaker(bind=engine))

def main():
	
	#reg = open("df1.csv")
	reg= open("dummy.csv")

	reader_reg = csv.reader(reg)
	next(reader_reg,None)

	print("iterating")


	for playdate,gametype,headshot,playtime,title,kill,damage,distance,walking_distance,ride_distance,DBNO,assists,heal,boost,revive,kill_per_min,head_per_kill in reader_reg:
		#print(DBNO)
		db.execute("INSERT INTO pros (playdate,gametype,headshot,playtime,title,kill,damage,distance,walking_distance,ride_distance,DBNO,assists,heal,boost,revive,kill_per_min,head_per_kill) VALUES (:playdate, :gametype, :headshot, :playtime,:title,:kill,:damage,:distance,:walking_distance,:ride_distance,:DBNO,:assists,:heal,:boost,:revive,:kill_per_min,:head_per_kill)",{"playdate": playdate, "gametype": gametype, "headshot": headshot,"playtime": playtime,"title": title, "kill": kill, "damage": damage,"distance": distance,"walking_distance": walking_distance,"ride_distance": ride_distance,"DBNO": DBNO,"assists": assists,"heal": heal,"boost": boost,"revive": revive,"kill_per_min":kill_per_min,"head_per_kill":head_per_kill})
		print(f"Added user: {title}")
	db.commit()
	
	#cheat = open("export_dataframe2.csv")
	#reader_cheat = csv.reader(cheat)

	#pro = open("export_dataframe3.csv")
	#reader_pro =csv.reader(pro)

	print("done")

if __name__ == "__main__":
	main()
