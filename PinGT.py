# -*- coding: utf-8 -*-

from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from database import connect_db, add_user, add_event, select_activity, drop_all_tables
from crawler import *

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

app.config.from_object(__name__)
db = MySQL()
db.init_app(app)

db_handler = connect_db(db)
db_handler.ensure_tables()

@app.route('/')
def show_entries():
    return render_template('show_entries.html')

'''
conduct heavy lifting work for events-related db communication
'''
@app.route('/events', methods=['GET', 'POST'])
def events():
    error = None
    if request.method == "GET":
        startDate = request.args.get('startDate', type=str)
        endDate = request.args.get('endDate', type=str)
        tag = request.args.get('tag', type=str)
        entries = select_activity(db_handler, startDate, endDate, tag)
        return jsonify(events=entries)
    elif request.method == "POST":
        name = request.json['name']
        date = request.json['date']
        time = request.json['time']
        tags = request.json['tags']
        location = request.json['location']
        latlon = request.json['latlon']
        description = request.json['description']
        pseudoID = '903066777'
        add_event(db_handler, name, pseudoID, location, latlon['lat'], latlon['lon'], \
                  date, time, description, tags)
        return "OK"
    return redirect(url_for('/'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        key_pairs = {}
        for row in db_handler.get_all_records(db_handler.user_tb):
            key_pairs[row[0]] = row[1]

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

    # populate user info into user table
    add_user(db_handler, id, password, gender == "male", major, grade == "undergraduate")
    print "current user table: "
    for row in db_handler.get_all_records(db_handler.user_tb):
        print row

    session['username'] = id
    session['logged_in'] = True
    return redirect(url_for('show_entries'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

def populateData(start_date, end_date):
    events = crawler(start_date, end_date)
    events = processGeoInfo(events)

    # populate data into db
    for e in events:
        try:
            add_event(db_handler, e['Name'], e['CreatorId'], e['Location'], e['latlon']['lat'], \
                e['latlon']['lng'], e['Date'], e['Time'], e['Description'], e['Tag'])
        except:
            continue

if __name__ == '__main__':
    app.run()