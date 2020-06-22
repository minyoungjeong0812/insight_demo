import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://sollsrywssgqwp:3c79a640882fb271f04b87c85e54e09c654059316404be7bcdb671cc6bf7976d@ec2-35-171-31-33.compute-1.amazonaws.com:5432/d77ns8sefglun7"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
