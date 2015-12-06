# -*- coding: utf-8 -*-

import re, time, datetime, pytz, smtplib
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from database import init_db, add_user, add_activity, select_activity, \
    get_activity, update_activity, delete_activity, add_notification, \
    get_notification
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
db_handler = init_db(app)
server = smtplib.SMTP( "smtp.gmail.com", 587 )
server.starttls()
server.login('cs6400project@gmail.com', 'CS6400PASSWORD')

@app.route('/')
def showEntries():
    return render_template('show_entries.html')

'''
conduct heavy lifting work for events-related db communication
'''
@app.route('/events', methods=['GET', 'POST', 'UPDATE', 'DELETE'])
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
        gtID = session['username']

        # some input checking
        if len(name) == 0 or len(date) == 0 or len(time) == 0 or len(tags) == 0 \
            or len(location) == 0 or (not isinstance(latlon, dict)) \
            or len(description) == 0 or len(gtID) == 0:
            return "Bad request", 400

        try:
            int(gtID)
        except:
            return "Bad request", 400

        if not isinstance(tags, list):
            return "Bad request", 400

        r = re.compile('.{4}-.{2}-.{2}')
        if not (len(date) == 10):
            return "Bad request", 400
        else:
            if not r.match(date):
                return "Bad request", 400

        add_activity(db_handler, name, gtID, location, latlon['lat'], latlon['lon'], \
                  date, time, description, tags)
        return "OK"
    elif request.method == "UPDATE":
        activityID = long(request.json['activityID'])
        name = request.json['name']
        date = request.json['date']
        time = request.json['time']
        tags = request.json['tags']
        description = request.json['description']

        # some input checking
        if len(name) == 0 or len(date) == 0 or len(time) == 0 or len(tags) == 0 \
            or len(description) == 0:
            return "Bad request", 400

        if not isinstance(tags, list):
            return "Bad request", 400

        r = re.compile('.{4}-.{2}-.{2}')
        if not (len(date) == 10):
            return "Bad request", 400
        else:
            if not r.match(date):
                return "Bad request", 400

        act = get_activity(db_handler, activityID)
        creatorID = act[2]
        gtID = long(session['username'])
        if gtID == creatorID:
            update_activity(db_handler, activityID, name, date, time, tags, description)
            return "OK"
        else:
            return "Not authorized", 403
    elif request.method == "DELETE":
        activityID = long(request.json['activityID'])
        print activityID
        act = get_activity(db_handler, activityID)
        creatorID = act[2]
        gtID = long(session['username'])
        print creatorID, gtID
        if gtID == creatorID:
            delete_activity(db_handler, activityID)
            return "OK"
        else:
            return "Not authorized", 403

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
            session['username'] = id
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/notification', methods=['GET', 'POST'])
def notification():
    error = None
    if request.method == "GET": # check whether there is upcoming events
        gtID = session['username']
        events = get_notification(db_handler, gtID)

        key_pairs = {}
        for row in db_handler.get_all_records(db_handler.user_tb):
            key_pairs[row[0]] = row[1:]
        user = key_pairs[long(gtID)]
        for e in events:
            minutes = calculateTimeLeft(e)
            if minutes < 600:
                pushNotification(user, e, minutes)
        return "OK"
    elif request.method == "POST": # subscribe an event
        activityID = request.json['activityID']
        gtID = session['username']
        print gtID, activityID

        # some input checking
        if len(gtID) == 0:
            return "Not authorized", 403
        try:
            int(gtID)
        except:
            return "Bad request", 400
        add_notification(db_handler, gtID, activityID)
        return "OK"

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

def calculateTimeLeft(e):
    start_time = e[5].strip().split('-')[0]
    HH, MM = start_time.split(':')
    MM = MM[0:2]
    if start_time[5:] == 'pm':
        HH = HH + 12
    start_time = str(HH) + '-' + MM
    start_date_string = str(e[4]) + "-" + start_time
    start_date = datetime.datetime.strptime(start_date_string, "%Y-%m-%d-%H-%M")
    today = datetime.datetime.now()
    diff = start_date - today
    minutes = diff.seconds / 60
    return minutes

def pushNotification(user, event, minutes):
    # TODO Replace this once user schema is changed
    phoneNumber = '14049403672'
    email = "glningwang@gmail.com"
    eventName = "Video games"
    eventLoc = "CRC"
    msg = "Hello from Pin@GT! The event %s you subscribe is upcoming! It will happen at %s in %s minutes." \
          % (eventName, eventLoc, minutes)
    server.set_debuglevel(10)
    server.sendmail('PIN@GT', [phoneNumber + '@tmomail.net'], msg)
    server.sendmail('PIN@GT', [email], msg)

def populateData(start_date, end_date):
    events = crawler(start_date, end_date)
    events = processGeoInfo(events)

    # populate data into db
    for e in events:
        try:
            add_activity(db_handler, e['Name'], e['CreatorId'], e['Location'], e['latlon']['lat'], \
                e['latlon']['lng'], e['Date'], e['Time'], e['Description'], e['Tag'])
        except:
            continue

if __name__ == '__main__':
    app.run()