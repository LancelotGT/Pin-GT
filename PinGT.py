# -*- coding: utf-8 -*-

import os
from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from database import connect_db, add_user
from utils import *

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    MYSQL_DATABASE_HOST='52.91.229.69',
    MYSQL_DATABASE_PORT=3306,
    MYSQL_DATABASE_USER='root',
    MYSQL_DATABASE_PASSWORD='CS6400',
    MYSQL_DATABASE_DB='PIN'
))

def test(test_db):
    db = connect_db(test_db)
    db.ensure_tables()
    # check the initial user_tb
    records = []
    for row in db.get_all_records(db.user_tb):
        records.append(row)
    print records
    # insert record and check
    add_user(db, db.user_tb, 903012347, "asdf", 0, 'ece', 0)
    for row in db.get_all_records(db.user_tb):
        records.append(row)
    print records

app.config.from_object(__name__)
db = MySQL()
db.init_app(app)

db_handler = connect_db(db)
db_handler.ensure_tables()

# test(db)

print "try to connect database..."
conn = db.connect()
print  "connection complete"
cur = conn.cursor()

def get_cursor():
    """Connects to the specific database."""
    return conn.cursor()

def commit():
    conn.commit()

def init_db():
    with app.open_resource('schema.sql', mode='r') as f:
        get_cursor().executescript(f.read())
    commit()

@app.route('/')
def show_entries():
    # cur = get_cursor()
    # cur.execute('select title, text from entries')
    # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]

    start_date='2015/11/17'
    end_date='2015/11/18'
    entries = getEventsByDay(start_date, end_date)
    locations = [entry['Location'] for entry in entries]
    print locations
    latlons = getGeoInfo(locations)
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    cur = get_cursor()
    queryStr = 'insert into entries (title, text) values ("%s", "%s")' \
               % (request.form['title'], request.form['text'])
    cur.execute(queryStr)
    commit()

    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        key_pairs = {}
        for row in db_handler.get_all_records(db_handler.user_tb):
            key_pairs[row[0]] = row[1]

        print "user:password pairs in db: ", key_pairs

        if int(request.form['username']) not in key_pairs.keys():
            error = 'Invalid username'
        elif request.form['password'] != key_pairs[int(request.form['username'])]:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'GET':
        return render_template('register.html', error=error)

    if request.method == 'POST':
        if len(request.form['id']) == 0:
            error = "GT ID cannot be empty"
            return render_template('register.html', error=error)
        if len(request.form['major']) == 0:
            error = "Major cannot be empty"
            return render_template('register.html', error=error)
        if len(request.form['password']) == 0:
            error = "Password cannot be empty"
            return render_template('register.html', error=error)

    id = request.form['id']
    password = request.form['password']
    grade = request.form['grade']
    major = request.form['major']
    gender = request.form['gender']
    print "Register input: ", id, password, grade, major, gender

    ### TODO Populate user input into database here
    add_user(db_handler, db_handler.user_tb, id, password, gender == "male", major, grade == "undergraduate")
    print "current user table: "
    for row in db_handler.get_all_records(db_handler.user_tb):
        print row
    session['logged_in'] = True
    return redirect(url_for('show_entries'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()

