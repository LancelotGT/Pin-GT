# -*- coding: utf-8 -*-

from flaskext.mysql import MySQL

'''
Several db connection helpers used by app view
'''
def init_db(app):
    db = MySQL()
    db.init_app(app)
    db_handler = connect_db(db)
    db_handler.ensure_tables()
    return db_handler

def connect_db(db_file):
    return DBWrapper(db_file)

# insert a new user
def add_user(db, gtId, password, gender, major, grade):
    iter_list = []
    iter_list.append((gtId, password, gender, major, grade))
    db.insert_rows(db.user_tb, user_schema, iter_list)

# insert a new event
def add_activity(db, activityName, createrId, locName, lat, lon, date, time, description, tags):

    if date == '00000000': # skip if no date provided
        return

    # insert location into location_tb
    loc_list = []
    loc_list.append((locName, lon, lat))
    db.insert_rows(db.location_tb, location_schema, loc_list)

    # insert into activity_tb
    iter_list = []
    iter_list.append((activityName, createrId, locName, date, time, description))
    db.insert_rows(db.activity_tb, activity_schema, iter_list)
    # insert into actTag_tb
    iter_list = []
    for tag in tags:
        activity_record = db.get_record_by_activityName(activityName, date)
        activityId = activity_record[0]
        iter_list.append((activityId, tag))
    db.insert_rows(db.actTag_tb, actTag_schema, iter_list)

# get activity given name and date
def get_activity(db, activityId):
    record = db.get_record_by_activityId(activityId)
    return record

def update_activity(db, activityId, name, date, time, tags, description):
    record = db.update_activity_by_Id(activityId, name, date, time, description)
    db.delete_tag_by_activityId(activityId)
    l = []
    for tag in tags:
        l.append((activityId, tag))
    db.insert_rows(db.actTag_tb, actTag_schema, l)
    return record

def delete_activity(db, activityId):
    db.delete_tag_by_activityId(activityId)
    db.delete_record_by_activityId(activityId)

def select_activity(db, start_date, end_date, tag):
    activityRecords = db.get_activity_by_date(start_date, end_date)
    responses = []
    for record in activityRecords:
        t = db.get_tag_by_activityId(record[0])
        loc = db.get_record_by_locationName(record[3])
        loc = (float(loc[1]), float(loc[2]))
        l = [e[1] for e in t]
        if tag in l or tag == 'All':
            d = {
                'ActivityId': record[0],
                'Name': record[1],
                'CreatorId': record[2],
                'Location': record[3],
                'Date': str(record[4]),
                'Time': record[5],
                'Description': record[6],
                'Tag': l,
                'latlon': loc
            }
            responses.append(d)
    return responses

def add_notification(db, gtID, activityID):
    l = []
    l.append((activityID, gtID))
    db.insert_rows(db.notification_tb, notification_schema, l)

def get_notification(db, gtID):
    record = db.get_notification_by_gtId(gtID)
    response = []
    for r in record:
        act = db.get_record_by_activityId(r[0])
        response.append(act)
    return response

def delete_notification(db, activityID, gtID):
    db.delete_notification_by_key(activityID, gtID)

def drop_all_tables(db):
    sql = "drop table " + db.notification_tb;
    db.exe(sql)
    sql = "drop table " + db.actTag_tb;
    db.exe(sql)
    sql = "drop table " + db.activity_tb;
    db.exe(sql)
    sql = "drop table " + db.location_tb;
    db.exe(sql)


'''
Private db stuff here
'''

user_schema = [
    ('gtId', 'INT NOT NULL'),
    ('password', 'VARCHAR(20) NOT NULL'),
    ('name', 'VARCHAR(30) NOT NULL'),
    ('gender', 'TINYINT(1) NOT NULL'),
    ('major', 'VARCHAR(30) NOT NULL'),
    ('grade', 'TINYINT(1) NOT NULL'),
    ('number', 'VARCHAR(20) NOT NULL'),
    ('email', 'VARCHAR(30) NOT NULL'),
    ('PRIMARY KEY', '(gtId)')        # PK
]

# tagId locationId
location_schema = [
    ('locName', 'VARCHAR(100) NOT NULL'),
    ('longitude', 'DOUBLE PRECISION NOT NULL'),
    ('latitude', 'DOUBLE PRECISION NOT NULL'),
    ('PRIMARY KEY', '(locName)')      
]

activity_schema = [
    ('activityId', 'INT NOT NULL AUTO_INCREMENT'),
    ('activityName', 'VARCHAR(150)'),
    ('gtId', 'INT NOT NULL'),
    ('locName', 'VARCHAR(50) NOT NULL'),      # different from progr report
    ('date', 'DATE NOT NULL'),      # FORMAT: 2011-01-01  ## 20150101
    ('time', 'VARCHAR(30)'),        # NOT SURE ABOUT THE TIME FORMAT
    ('description', 'TEXT'),
    ('PRIMARY KEY', '(activityId)'),
    ('FOREIGN KEY', '(gtId) REFERENCES user_tb (gtId)'),
    ('FOREIGN KEY', '(locName) REFERENCES location_tb (locName)')
]


# suppose an activity could have several tags
actTag_schema = [
    ('activityId', 'INT NOT NULL'),
    ('tag', 'VARCHAR(30) NOT NULL'),
    ('PRIMARY KEY', '(activityId, tag)'),
    ('FOREIGN KEY', '(activityId) REFERENCES activity_tb (activityId)')
]

# suppose only send notification once (differenr from progr report)
notification_schema = [
    ('activityId', 'INT NOT NULL'),
    ('gtId', 'INT NOT NULL'),
    ('PRIMARY KEY', '(activityId, gtId)'),
    ('FOREIGN KEY', '(activityId) REFERENCES activity_tb (activityId)'),
    ('FOREIGN KEY', '(gtId) REFERENCES user_tb (gtId)')
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
        self.actTag_tb = 'actTag_tb'
        self.notification_tb = 'notification_tb'
        self.conn()

    def conn(self):
        if self.connection is not None:
            self.connection.commit()
            self.connection.close()
        self.connection = self.db_file.connect()
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
        self.exe(self._build_create_table_sql(self.actTag_tb, actTag_schema))
        self.exe(self._build_create_table_sql(self.notification_tb, notification_schema))      

    def _build_insert_sql(self, tb_name, schema):
        if tb_name == 'user_tb' or tb_name == 'location_tb':
            question_marks = ', '.join(['%s'] * (len(schema) - 1))
            return "INSERT IGNORE INTO {0} VALUES ({1})".format(tb_name, question_marks)
        # activity_tb, notification_schema
        elif tb_name == 'activity_tb':
            question_marks = ', '.join(['%s'] * (len(schema) - 4))
            col_insert = []
            for i, col in enumerate(schema):
                if i in range(1, len(schema) - 3):
                    col_insert.append(schema[i][0])
            col_insert_str = ', '.join(col_insert)
            col_insert_str = '(' + col_insert_str + ')'
            return "INSERT IGNORE INTO {0} VALUES ({1})".format(tb_name + col_insert_str, question_marks)
        # actTag_schema
        elif tb_name == 'notification_tb':
            question_marks = ', '.join(['%s'] * (len(schema) - 3))
            col_insert = []
            for i, col in enumerate(schema):
                if i in range(0, len(schema) - 3):
                    col_insert.append(schema[i][0])
            col_insert_str = ', '.join(col_insert)
            col_insert_str = '(' + col_insert_str + ')'
            return "INSERT IGNORE INTO {0} VALUES ({1})".format(tb_name + col_insert_str, question_marks)
        else:
            question_marks = ', '.join(['%s'] * (len(schema) - 2))
            col_insert = []
            for i, col in enumerate(schema):
                if i in range(0, len(schema) - 2):
                    col_insert.append(schema[i][0])
            col_insert_str = ', '.join(col_insert)
            col_insert_str = '(' + col_insert_str + ')'
            return "INSERT IGNORE INTO {0} VALUES ({1})".format(tb_name + col_insert_str, question_marks)

    def exe(self, sql, params=None):
        if params:
            return self.c.execute(sql, params)
        else:
            return self.c.execute(sql)

    def commit(self):
        self.connection.commit()
        self.c = self.connection.cursor()

    def insert_rows(self, tb_name, schema, iter_list):
        sql = self._build_insert_sql(tb_name, schema)
        print sql
        for values in iter_list:
            self.c.execute(sql, tuple(values))
        self.commit()

    def get_all_records(self, table):
        sql = "SELECT * FROM {0}".format(table)
        self.exe(sql)
        return self.c.fetchall()

    def get_record_by_id(self, table, schema, id):
        sql = ("SELECT * FROM {0} WHERE " + str(schema[0][0]) + " = %s").format(table)
        self.exe(sql, (id,))
        return self.c.fetchone()

    def get_record_by_activityName(self, activityName, date):
        sql = ("SELECT * FROM {0} WHERE " + str(activity_schema[1][0]) + " = %s" + " AND " + str(activity_schema[4][0]) + " = %s").format(self.activity_tb)
        self.exe(sql, (activityName, date))
        return self.c.fetchone()

    def get_record_by_activityId(self, activityId):
        sql = ("SELECT * FROM {0} WHERE " + str(activity_schema[0][0]) + " = %s").format(self.activity_tb)
        self.exe(sql, (activityId, ))
        return self.c.fetchone()

    def get_record_by_locationName(self, locationName):
        sql = ("SELECT * FROM {0} WHERE " + str(location_schema[0][0]) + " = %s").format(self.location_tb)
        self.exe(sql, (locationName, ))
        return self.c.fetchone()

    # get event according to start date, end date and tags
    def get_activity_by_date(self, start_date, end_date):
        sql = ("SELECT * FROM {0} WHERE " + str(activity_schema[4][0]) + " between %s" + " AND %s").format(self.activity_tb)
        self.exe(sql, (start_date, end_date))
        return self.c.fetchall()

    def get_tag_by_activityId(self, activityId):
        sql = ("SELECT * FROM {0} WHERE " + str(actTag_schema[0][0]) + " = %s").format(self.actTag_tb)
        self.exe(sql, (activityId, ))
        return self.c.fetchall()

    def get_user_by_gtId(self, gtId):
        sql = ("SELECT * FROM {0} WHERE " + str(user_schema[0][0]) + " = %s").format(self.user_tb)
        self.exe(sql, (gtId, ))
        return self.c.fetchone()

    def get_notification_by_gtId(self, gtId):
        sql = ("SELECT * FROM {0} WHERE " + str(notification_schema[1][0]) + " = %s").format(self.notification_tb)
        self.exe(sql, (gtId, ))
        return self.c.fetchall()

    def delete_record_by_activityId(self, activityId):
        sql = ("DELETE FROM {0} WHERE " + str(activity_schema[0][0]) + " = %s").format(self.activity_tb)
        self.exe(sql, (activityId, ))
        self.commit()

    def delete_tag_by_activityId(self, activityId):
        sql = ("DELETE FROM {0} WHERE " + str(actTag_schema[0][0]) + " = %s").format(self.actTag_tb)
        self.exe(sql, (activityId, ))
        self.commit()

    def delete_notification_by_key(self, activityId, gtId):
        sql = ("DELETE FROM {0} WHERE " + str(notification_schema[0][0]) + " = %s AND " + \
               str(notification_schema[1][0]) + " = %s").format(self.notification_tb)
        self.exe(sql, (activityId, gtId))
        self.commit()

    def update_activity_by_Id(self, activityId, name, date, time, description):
        sql = ("UPDATE {0} SET activityName=%s, date=%s, time=%s, description=%s ")\
            .format(self.activity_tb)
        sql += "WHERE " + str(activity_schema[0][0]) + "=%s"
        self.exe(sql, (name, date, time, description, activityId))
        self.commit()