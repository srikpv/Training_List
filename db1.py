import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect
from sqlalchemy.sql import text
import json
import csv
from sqlalchemy.sql.sqltypes import DateTime

bad_chars = ['ï', '»', '¿']
files = ["Technical.csv", "PM.csv"]

with open("config.json") as f:
    data = json.load(f)
engine = create_engine(data["SQLALCHEMY_DATABASE_URI"])

metadata = MetaData()

training_category = Table("training_category", metadata,
                            Column("id", Integer, primary_key = True),
                            Column("category", String),
                        )
training_knowledge_area = Table("training_knowledge_area", metadata,
                            Column("id", Integer, primary_key = True),
                            Column("knowledge_area", String),
                        )
training = Table("training", metadata,
                    Column("id", Integer, primary_key = True),
                    Column("category_id", String),
                    Column("knowledge_area_id", String),
                    Column("title", String),
                    Column("link", String),
                    Column("description", String),
                    Column("free", Integer),
                    Column("advanced", Integer),
                )
user = Table("user", metadata,
                Column("id", Integer, primary_key = True),
                Column("name", String),
                Column("email", String),
             )
training_assignment = Table("training_assignment", metadata,
                                Column("id", Integer, primary_key = True),
                                Column("training_id", Integer),
                                Column("user_id", Integer),
                                Column("approver_id", Integer),
                                Column("approved", Integer),
                                Column("date_approved", DateTime),
                                Column("finance_approved", Integer),
                                Column("finance_approved_by", Integer),
                                Column("finance_date_approved", DateTime),
                            )
approver = Table("approver", metadata,
                    Column("id", Integer, primary_key = True),
                    Column("name", String),
                    Column("email", String),
                    Column("code", String),
                )
finance_approver = Table("finance_approver", metadata,
                            Column("id", Integer, primary_key = True),
                            Column("name", String),
                            Column("email", String),
                            Column("code", String),
                         )
metadata.create_all(engine)

def get_id(table, column, value, connection):
    query_str = "SELECT id FROM %s where %s.%s = :x" % (table, table, column)
    query = text(query_str)    
    value = ''.join(i for i in value if not i in bad_chars)
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

for filename in files:
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')    
        for csv_row in readCSV:
            with engine.connect() as con:
                ###########Insert category
                category_id = get_id("training_category", "category", csv_row[0], con)
                # ###########Insert knowledge_area
                knowledge_area_id = get_id("training_knowledge_area", "knowledge_area", csv_row[1], con)
                # ###########Insert Training
                query = text("INSERT INTO training (category_id, knowledge_area_id, title, link, description, free, advanced) VALUES (:cat_id, :ka_id, :title, :link, :description, :free, :advanced)")
                rs = con.execute(query, cat_id = category_id, ka_id = knowledge_area_id, title = csv_row[2], link = csv_row[3], description = csv_row[4], free = (1 if csv_row[5].lower() == "yes" else 0), advanced = (1 if csv_row[6].lower() == "advanced" else 0))
