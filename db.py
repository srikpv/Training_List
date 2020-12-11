from os import stat
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect
from sqlalchemy import engine
from sqlalchemy.sql import text
import json
import csv
from sqlalchemy.sql.sqltypes import DateTime
from Classes import Training_Category, Training_Knowledge_Area, Training, Training_Assignment, User, Approver
from datetime import datetime

class DB:
    
    @staticmethod
    def get_engine():        
        engine = create_engine("sqlite:///training.db")
        return engine
    
    @staticmethod
    def get_trainings():
        engine = DB.get_engine()
        trainings = []
        with engine.connect() as con:
            query = text(
                        "SELECT training.id, training_category.category, training_knowledge_area.knowledge_area, training.title, training.link, training.description, training.free, training.advanced "
                        "FROM training, training_category, training_knowledge_area "
                        "WHERE training.category_id = training_category.id "
                        "AND training.knowledge_area_id = training_knowledge_area.id "
                    )    
            rs = con.execute(query).fetchall()
            for row in rs:
                training = Training(row["id"], row["category"], row["knowledge_area"], row["title"], row["link"], row["description"], row["free"], row["advanced"])
                trainings.append(training)
        return trainings
    
    @staticmethod
    def get_knowledge_areas():
        engine = DB.get_engine()
        knowledge_areas = []
        with engine.connect() as con:
            query = text(
                        "SELECT training_knowledge_area.id, training_knowledge_area.knowledge_area "
                        "FROM training_knowledge_area "
                    )    
            rs = con.execute(query).fetchall()
            for row in rs:
                knowledge_area = Training_Knowledge_Area(row["id"], row["knowledge_area"])
                knowledge_areas.append(knowledge_area)
        return knowledge_areas
    
    @staticmethod
    def verify_user(email):
        engine = DB.get_engine()
        with engine.connect() as con:
            query = text(
                        "SELECT user.id "
                        "FROM user "
                        "WHERE LOWER(user.email) = :x"
                    )    
            rs = con.execute(query, x=email.lower()).fetchall()
            if(len(rs)) > 0:
                return [row[0] for row in rs][0]
            else:
                return 0
        
    @staticmethod
    def add_user(name, email):
        engine = DB.get_engine()
        with engine.connect() as con:
            query = text(
                        "SELECT user.id, user.name, user.email "
                        "FROM user "
                        "WHERE user.email = :x AND user.name = :y"
                    )    
            rs = con.execute(query, x=email, y=name).fetchall()
            if(len(rs)) > 0:
                return [row[0] for row in rs][0]
            else:
                query_str = "INSERT INTO user (name, email) VALUES (:y, :x)"
                query = text(query_str)
                rs = con.execute(query, x=email, y=name)
                query = text(
                        "SELECT user.id, user.name, user.email "
                        "FROM user "
                        "WHERE user.email = :x AND user.name = :y"
                        )    
                rs = con.execute(query, x=email, y=name).fetchall()
                if(len(rs)) > 0:
                    return [row[0] for row in rs][0]

    @staticmethod
    def add_new_trainings(user_id, new_trainings, approver_id):
        training_ids = []
        engine = DB.get_engine()
        with engine.connect() as con:
            for i in range(len(new_trainings)):
                training = Training(0, new_trainings[i]["category"], new_trainings[i]["knowledge_area"], new_trainings[i]["title"], new_trainings[i]["link"], new_trainings[i]["description"], new_trainings[i]["free"], 0)
                ###########Insert category
                category_id = DB.get_id("training_category", "category", training.category, con)
                # ###########Insert knowledge_area
                knowledge_area_id = DB.get_id("training_knowledge_area", "knowledge_area", training.knowledge_area, con)
                # ###########Insert Training
                query = text("INSERT INTO training (category_id, knowledge_area_id, title, link, description, free, advanced) VALUES (:cat_id, :ka_id, :title, :link, :description, :free, :advanced)")
                rs = con.execute(query, cat_id = category_id, ka_id = knowledge_area_id, title = training.title, link = training.link, description = training.description, free = training.free, advanced = 0)
                query = text("SELECT MAX(id) FROM training WHERE category_id = :cat_id AND knowledge_area_id = :ka_id AND title = :title AND link = :link AND description = :description AND free = :free AND advanced = :advanced")
                rs = con.execute(query, cat_id = category_id, ka_id = knowledge_area_id, title = training.title, link = training.link, description = training.description, free = training.free, advanced = 0)
                training_id = [row[0] for row in rs][0]   
                training_ids.append(training_id)
        DB.assign_trainings(user_id, training_ids, approver_id)
                
    @staticmethod
    def assign_trainings(user_id, training_ids, approver_id):
        engine = DB.get_engine()
        with engine.connect() as con:
            for training_id in training_ids:
                query = text("INSERT INTO training_assignment (training_id, user_id, approver_id)  VALUES(:x, :y, :z)")
                rs = con.execute(query, x = training_id, y = user_id, z = approver_id)
    
    @staticmethod
    def get_id(table, column, value, connection):
        query_str = "SELECT id FROM %s where %s.%s = :x" % (table, table, column)
        query = text(query_str)    
        rs = connection.execute(query, x=value).fetchall()
        if(len(rs) > 0):
            id = [row[0] for row in rs][0]
        else:
            query_str = "INSERT INTO %s (%s) VALUES (:x)" % (table, column)
            query = text(query_str)
            rs = connection.execute(query, x=value)
            query_str = "SELECT id FROM %s where %s.%s = :x" % (table, table, column)
            query = text(query_str)
            rs = connection.execute(query, x=value).fetchall()
            id = [row[0] for row in rs][0]
        return id
    
    @staticmethod
    def get_training_assignments(approver_id):
        engine = DB.get_engine()
        training_assignments = []
        with engine.connect() as con:
            query = text(
                        "SELECT training_assignment.id, training.id as training_id, training_category.category, training_knowledge_area.knowledge_area, "
                        "training.title, training.link, training.description, training.free, training.advanced, user.name, user.email, user.id as user_id "
                        "FROM training_assignment, training, training_category, training_knowledge_area, user "
                        "WHERE training_assignment.training_id = training.id AND training.category_id = training_category.id "
                        "AND training.knowledge_area_id = training_knowledge_area.id AND (training_assignment.approved IS NULL OR training_assignment.approved = 0) "
                        "AND training_assignment.user_id = user.id AND training_assignment.approver_id = :x "
                        "ORDER BY user.id, training_category.id, training_knowledge_area.id, training.id "
                    )    
            rs = con.execute(query, x = approver_id).fetchall()
            for row in rs:
                #(self, id, training_id, category, knowledge_area, title, link, description, free, advanced, user_id, name, email, approved, approved_by, date_approved, finance_approved, finance_approved_by, finance_date_approved)
                training_assignment = Training_Assignment(row["id"], row["training_id"], row["category"], row["knowledge_area"], row["title"], row["link"], row["description"], row["free"], row["advanced"], row["user_id"], row["name"], row["email"], 0, 0, "", 0, 0, "")
                training_assignments.append(training_assignment)
        return training_assignments
    
    @staticmethod
    def approve_trainings(approver_id, assigned_training_ids):
        engine = DB.get_engine()
        with engine.connect() as con:
            for assigned_training_id in assigned_training_ids:
                query = text("UPDATE training_assignment SET approved = 1, approver_id = :x, date_approved = :y "
                            "WHERE id IN (:z)"
                            )
                rs = con.execute(query, x = approver_id, y = datetime.now(), z = assigned_training_id)   
    
    @staticmethod
    def get_training_assignments_finance(approver_id):
        engine = DB.get_engine()
        training_assignments = []
        with engine.connect() as con:
            query = text(
                        "SELECT training_assignment.id, training.id as training_id, training_category.category, training_knowledge_area.knowledge_area, "
                        "training.title, training.link, training.description, training.free, training.advanced, user.name, user.email, user.id as user_id "
                        "FROM training_assignment, training, training_category, training_knowledge_area, user "
                        "WHERE training_assignment.training_id = training.id AND training.category_id = training_category.id AND (training.free IS NULL OR training.free = 0) "
                        "AND training.knowledge_area_id = training_knowledge_area.id AND training_assignment.approved = 1 AND (training_assignment.finance_approved IS NULL OR training_assignment.finance_approved = 0) "
                        "AND training_assignment.user_id = user.id "
                        "ORDER BY user.id, training_category.id, training_knowledge_area.id, training.id "
                    )    
            rs = con.execute(query).fetchall()
            for row in rs:
                #(self, id, training_id, category, knowledge_area, title, link, description, free, advanced, user_id, name, email, approved, approved_by, date_approved, finance_approved, finance_approved_by, finance_date_approved)
                training_assignment = Training_Assignment(row["id"], row["training_id"], row["category"], row["knowledge_area"], row["title"], row["link"], row["description"], row["free"], row["advanced"], row["user_id"], row["name"], row["email"], 0, 0, "", 0, 0, "")
                training_assignments.append(training_assignment)
        return training_assignments
    
    @staticmethod
    def approve_trainings_finance(approver_id, assigned_training_ids):
        engine = DB.get_engine()
        with engine.connect() as con:
            for assigned_training_id in assigned_training_ids:
                print(assigned_training_id)
                query = text("UPDATE training_assignment SET finance_approved = 1, finance_approved_by = :x, finance_date_approved = :y "
                            "WHERE id IN (:z)"
                            )
                rs = con.execute(query, x = approver_id, y = datetime.now(), z = assigned_training_id)   
    
            # query = text("UPDATE training_assignment SET approved = 1, approver_id = :x, date_approved = :y "
            #              "WHERE id IN :z"
            #              )
            # print(query)
            # rs = con.execute(query, x = approver_id, y = datetime.now(), z = assigned_training_ids)
            # print(rs)
    
    @staticmethod
    def get_approvers():
        approvers = []
        engine = DB.get_engine()
        with engine.connect() as con:
            query = text(
                        "SELECT id, name, email "
                        "FROM approver "
                    )    
            rs = con.execute(query).fetchall()
            for row in rs:
                approver = Approver(row["id"], row["name"], row["email"], "")
                approvers.append(approver)
        return approvers
    
    @staticmethod
    def get_approver(email):
        engine = DB.get_engine()
        with engine.connect() as con:
            query = text(
                        "SELECT id, name, email, code "
                        "FROM approver "
                        "WHERE email = :x"
                    )    
            rs = con.execute(query, x = email).fetchall()
            if(len(rs) > 0):
                approver = Approver(rs[0]["id"], rs[0]["name"], rs[0]["email"], rs[0]["code"])
            else:
                approver = Approver(0, "", "", "")
        return approver
    
    @staticmethod
    def get_approver_finance(email):
        engine = DB.get_engine()
        with engine.connect() as con:
            query = text(
                        "SELECT id, name, email, code "
                        "FROM finance_approver "
                        "WHERE email = :x"
                    )    
            rs = con.execute(query, x = email).fetchall()
            if(len(rs) > 0):
                approver = Approver(rs[0]["id"], rs[0]["name"], rs[0]["email"], rs[0]["code"])
            else:
                approver = Approver(0, "", "", "")
        return approver