# -*- coding: utf-8 -*-
import os
from flaskext.mysql import MySQL
# import MySQLdb

def connect_db(db_file):
    return DBWrapper(db_file)

# insert a new user
def add_user(db, user_tb, gtId, password, gender, major, grade):
    iter_list = []
    iter_list.append((gtId, password, gender, major, grade))
    db.insert_rows(user_tb, user_schema, iter_list)

user_schema = [
    ('gtId', 'INT NOT NULL'),
    ('password', 'VARCHAR(20) NOT NULL'),
    #('name', 'VARCHAR(30) NOT NULL'),      # maybe add it later
    ('gender', 'TINYINT(1) NOT NULL'),
    ('major', 'VARCHAR(30) NOT NULL'),
    ('grade', 'TINYINT(1) NOT NULL'),
    ('PRIMARY KEY', '(gtId)')        # PK

]

location_schema = [
    ('locationId', 'INT NOT NULL'),
    ('longitude', 'FLOAT NOT NULL'),
    ('latitude', 'FLOAT NOT NULL'),
    ('name', 'VARCHAR(50) NOT NULL'),
    ('PRIMARY KEY', '(locationId)')      
]

activity_schema = [
    ('activityId', 'INT NOT NULL'),
    ('locationId', 'INT NOT NULL'),      # different from progr report
    ('date', 'DATE NOT NULL'),      # FORMAT: 2011-01-01
    ('time', 'VARCHAR(30)'),        # NOT SURE ABOUT THE TIME FORMAT
    ('description', 'TEXT'),
    ('source', 'VARCHAR(50)'),
    ('PRIMARY KEY', '(activityId)')      
]

tag_schema = [
    ('tagId', 'INT NOT NULL'),
    ('tag', 'VARCHAR(50) NOT NULL'),
    ('PRIMARY KEY', '(tagId)')       
]

# suppose an activity could have several tags
actTag_schema = [
    ('Id', 'INT NOT NULL'),
    ('activityId', 'INT NOT NULL'),
    ('tagId', 'INT NOT NULL'),
    ('PRIMARY KEY', '(Id)')       
]

# suppose only send notification once (differenr from progr report)
notification_schema = [
    ('notificationId', 'INT NOT NULL'),
    ('locationId', 'INT NOT NULL'),
    ('gtId', 'INT NOT NULL'),
    ('time', 'DATETIME NOT NULL'),      # FORMAT: 2011-12-31 23:59:59
    ('PRIMARY KEY', '(notificationId)')
]


class DBWrapper(object):
    """
        Wrapper class to store & retrieve dataset with sqlite3.
    """
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
        self.c = None

        self.user_tb = 'user_tb'
        self.location_tb = 'location_tb'
        self.activity_tb = 'activity_tb'
        self.tag_tb = 'tag_tb'
        self.actTag_tb = 'actTag_tb'
        self.notification_tb = 'notification_tb'

        self.conn()

    def conn(self):
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
        self.connection = self.connect()
        print  "connection complete"
        self.c = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.commit()
            self.connection.close()

    # create table
    def _build_create_table_sql(self, tb_name, schema):
        col_names = ', '.join([c[0] + ' ' + c[1] for c in schema])
        return "CREATE TABLE IF NOT EXISTS {0} ({1})".format(tb_name, col_names)

    # create all the tables at beginning
    def ensure_tables(self):
        self.exe(self._build_create_table_sql(self.user_tb, user_schema))
        self.exe(self._build_create_table_sql(self.location_tb, location_schema))
        self.exe(self._build_create_table_sql(self.activity_tb, activity_schema))
        self.exe(self._build_create_table_sql(self.tag_tb, tag_schema))
        self.exe(self._build_create_table_sql(self.actTag_tb, actTag_schema))
        self.exe(self._build_create_table_sql(self.notification_tb, notification_schema))      


    def _build_insert_sql(self, tb_name, schema):
        question_marks = ', '.join(['%s'] * (len(schema) - 1))      # length -1 since the last element of schema is pk
        return "INSERT INTO {0} VALUES ({1})".format(tb_name, question_marks)


    def exe(self, sql, params=None):
        if params:
            return self.c.execute(sql, params)
        else:
            return self.c.execute(sql)


    def commit(self):
        self.connection.commit()
        self.c = self.connection.cursor()


    def instert_rows(self, tb_name, schema, iter_list):
        sql = self._build_insert_sql(tb_name, schema)
        for values in iter_list:
            self.c.execute(sql, tuple(values))
        self.commit()

    def get_all_records(self, table):
        sql = "SELECT * FROM {0}".format(table)
        return self.exe(sql)

    def get_record_by_id(self, table, schema):
        sql = ("SELECT * FROM {0} WHERE " + str(schema[0][0]) + " = %s").format(table)
        self.exe(sql, (Id))
        return self.c.fetchone()
        

    '''def update_record_by_id(self, table, Id, updates):
        sql = "UPDATE {0} SET nickname=?, accuracy=?, rmse=?, submission=?, \
         time=? WHERE andrew_id=?".format(table)
        self.exe(sql, (updates['nickname'], updates['accuracy'], updates['rmse'],
            updates['submission'], updates['time'], updates['andrew_id']))
        self.commit()'''

    '''
    def create_index(self, tb_name, schema):
        sql = "CREATE INDEX {0}_idx ON {1} ({0})".format(col_name, tb_name)
        self.exe(sql)
        self.commit()
    '''



