import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# class all_users(db.Model):
# 	__tablename__ = "all_users"
# 	key = db.Column(db.Integer, primary_key=True)


# 	gametype = db.Column(db.String, nullable=False)

# 	head_bin = db.Column(db.Integer, nullable=False)

# 	title = db.Column(db.String, nullable=False)

# 	username = db.Column(db.String, nullable=False)

# 	kill_bin = db.Column(db.Integer, nullable=False)

# 	damage_bin = db.Column(db.Integer, nullable=False)

# 	kpm_bin = db.Column(db.Integer, nullable=False)

# 	hpk_bin = db.Column(db.Integer, nullable=False)

# 	dist_bin = db.Column(db.Integer, nullable=False)

# 	playdate = db.Column(db.DateTime, nullable=False)


class all_users_raw(db.Model):
	__tablename__ = "all_users_raw"
	key = db.Column(db.Integer, primary_key=True)

	playdate = db.Column(db.DateTime, nullable=False)

	gametype = db.Column(db.String, nullable=False)

	headshot = db.Column(db.Integer, nullable=False)

	playtime = db.Column(db.Float, nullable=False)

	title = db.Column(db.String, nullable=False)

	kill = db.Column(db.Integer, nullable=False)

	damage = db.Column(db.Integer, nullable=False)

	distance = db.Column(db.Float, nullable=False)

	walking_distance = db.Column(db.Float, nullable=False)

	ride_distance = db.Column(db.Float, nullable=False)

	dbno = db.Column(db.Integer, nullable=False)

	assists = db.Column(db.Integer, nullable=False)

	heal = db.Column(db.Integer, nullable=False)

	boost = db.Column(db.Integer, nullable=False)

	revive = db.Column(db.Integer, nullable=False)

