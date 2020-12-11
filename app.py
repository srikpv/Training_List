from enum import unique
import re
from flask import Flask, render_template, request, url_for, make_response, jsonify
import json
from Classes import Training_Category, Training_Knowledge_Area, Training, Training_Assignment, User, Approver
from db import DB

app = Flask(__name__)

@app.route("/", methods = ["GET"])
def index():
    trainings = DB.get_trainings()
    categories_knowledge_list = {}
    for training in trainings:
        if training.category in categories_knowledge_list:
            if training.knowledge_area not in categories_knowledge_list[training.category]:
                categories_knowledge_list[training.category].append(training.knowledge_area)
        else:
            categories_knowledge_list[training.category] = []
            categories_knowledge_list[training.category].append(training.knowledge_area)
    approvers = DB.get_approvers()
    return render_template("index.html", trainings = trainings, categories_knowledge_list = categories_knowledge_list, approvers = approvers)

@app.route("/submit", methods = ["POST"])
def save_user_trainings():
    try:
        req_data = request.get_json()
        user_id = DB.add_user(req_data["name"], req_data["email"])
        selected_trainings = req_data["selected_training_ids"]
        approver_id = req_data["approver_id"]
        DB.assign_trainings(user_id, selected_trainings, approver_id)
        new_trainings = req_data["new_trainings"]
        if len(new_trainings) > 0:
            DB.add_new_trainings(user_id, new_trainings, approver_id)
        return make_response("", 200, {})
    except:
        return make_response("", 400, {})
    #

@app.route("/success", methods=["GET"])
def success():
    return render_template("success.html")

@app.route("/failure", methods=["GET"])
def failure():
    return render_template("failure.html")

@app.route("/verifyuser", methods=["GET"])
def verify_user():
    email = request.args.get('email')
    user_id = DB.verify_user(email)
    return make_response(jsonify(user_id), 200 if user_id == 0 else 400, {})

@app.route("/approve", methods = ["GET"])
def get_approve_trainings():
    if request.authorization and request.authorization.username != "":
        approver = DB.get_approver(request.authorization.username)
        if request.authorization.username == approver.email and request.authorization.password == approver.code and approver.id != 0:
            approver.code = ""
            training_assignments = DB.get_training_assignments(approver.id)
            return render_template("approve.html", training_assignments = training_assignments, approver = approver)
    return make_response("Incorrect Credentials", 401, {"WWW-Authenticate" : "Basic realm='Login Required'"})

@app.route("/approvetraining", methods = ["POST"])
def approve_user_trainings():
    try:
        req_data = request.get_json()
        assigned_training_ids = req_data["assigned_training_ids"]
        approver_id = req_data["approver_id"]
        DB.approve_trainings(approver_id, assigned_training_ids)
        return make_response("", 200, {})
    except:
        return make_response("", 400, {})

@app.route("/financeapprove", methods = ["GET"])
def finance_get_approve_trainings():
    if request.authorization and request.authorization.username != "":
        approver = DB.get_approver_finance(request.authorization.username)
        if request.authorization.username == approver.email and request.authorization.password == approver.code and approver.id != 0:
            approver.code = ""
            training_assignments = DB.get_training_assignments_finance(approver.id)
            return render_template("finance_approve.html", training_assignments = training_assignments, approver = approver)
    return make_response("Incorrect Credentials", 401, {"WWW-Authenticate" : "Basic realm='Login Required'"})

@app.route("/finance_approvetraining", methods = ["POST"])
def finance_approve_user_trainings():
    try:
        req_data = request.get_json()
        assigned_training_ids = req_data["assigned_training_ids"]
        approver_id = req_data["approver_id"]
        DB.approve_trainings_finance(approver_id, assigned_training_ids)
        return make_response("", 200, {})
    except:
        return make_response("", 400, {})


if __name__ == "__main__":
    app.debug = True
    app.run()