import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class reg_users(db.Model):
	__tablename__ = "reg_users"
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

	kill_per_min = db.Column(db.Float, nullable=False)

	head_per_kill = db.Column(db.Float, nullable=False)


class cheaters(db.Model):

	__tablename__ = "cheaters"
	
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

	kill_per_min = db.Column(db.Float, nullable=False)

	head_per_kill = db.Column(db.Float, nullable=False)


class pros(db.Model):
	__tablename__ = "pros"
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

	kill_per_min = db.Column(db.Float, nullable=False)

	head_per_kill = db.Column(db.Float, nullable=False)
