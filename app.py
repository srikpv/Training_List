from enum import unique
from flask import Flask, render_template, request
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.sql.schema import UniqueConstraint

with open("config.json") as f:
    data = json.load(f)
    

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = data["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Training(db.Model):
    training_id = db.Column(db.Integer, primary_key = True)
    training_category = db.Column(db.String(200))
    training_knowledge_are = db.Column(db.String(200))
    training_title = db.Column(db.String(300))
    training_link = db.Column(db.String(1000))
    training_description = db.Column(db.String(1000))
    is_deleted = db.Column(db.Boolean, default = False)
    
    def __init__(self, training_category, training_knowledge_are, training_title, training_link, training_description):
        self.training_category = training_category
        self.training_knowledge_are = training_knowledge_are
        self.training_title = training_title
        self.training_link = training_link
        self.training_description = training_description

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    user_sso = db.Column(db.String(10), unique = True, nullable = False)
    user_name = db.Column(db.String(200), nullable = False)
    user_email = db.Column(db.String(200), nullable = False)
    trainings = db.relationship("Assigned_Training", backref=db.backref('user', lazy='joined'), lazy = 'select')
    
    def __init__(self, user_sso, user_name, user_email):
        self.user_sso = user_sso
        self.user_name = user_name
        self.user_email = user_email

class Assigned_Training(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    training_id = db.Column(db.Integer, db.ForeignKey('training.training_id'), nullable = False)
    is_deleted = db.Column(db.Boolean, default = False)
    
    def __init__(self, user_id, training_id):
        self.user_id = user_id
        self.training_id = training_id

@app.route("/", methods = ["GET"])
def index():
    
    print("SQLALCHEMY_DATABASE_URI", app.config["SQLALCHEMY_DATABASE_URI"])
    return render_template("index.html")

if __name__ == "__main__":
    app.debug = True
    app.run()