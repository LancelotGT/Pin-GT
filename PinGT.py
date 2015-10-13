# -*- coding: utf-8 -*-

import os
from flaskext.mysql import MySQL
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    MYSQL_DATABASE_HOST='localhost',
    MYSQL_DATABASE_PORT=3306,
    MYSQL_DATABASE_USER='root',
    MYSQL_DATABASE_PASSWORD='',
    MYSQL_DATABASE_DB='PIN'
))

app.config.from_object(__name__)
db = MySQL()
db.init_app(app)
conn = db.connect()

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
    cur = get_cursor()
    cur.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
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
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
