import re
from flask import Flask, jsonify
from flask import render_template
from flask import request
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

connection = sqlite3.connect('booking.db')
connection.execute('create table if not exists users (id integer primary key, fname text not null, lname text not null, email text not null, username text not null, password text not null)')
connection.execute('create table if not exists Bookings (id integer primary key, departure text not null, destination text not null, traveldate DATE not null, passengers integer not null)')
connection.execute('create table if not exists Contact (id integer primary key, fullname text not null, email text not null, message text not null)')

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/booking", methods=["GET", "POST"])
def booking():
    errors = ''
    if request.method == 'POST':
        departure = request.form['departure']
        destination = request.form['destination']
        traveldate = request.form['traveldate']
        passengers = request.form['passengers']
        if not departure or not destination or not traveldate or not passengers:
            errors = 'Please Enter all the fields'
        elif datetime.strptime(traveldate, '%Y-%m-%d').date() < date.today():
            errors = 'Travel date must be after todays date'
        if not errors:
            connection = sqlite3.connect('booking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("insert into Bookings (departure, destination, traveldate, passengers) values (?, ?, ?, ?)", (departure, destination, traveldate, passengers))
            connection.commit()
            return jsonify(success = True)
        else:
            return jsonify(errors = errors)
    elif request.method == 'GET':
        return render_template('booking.html')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    errors = ''
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        message = request.form['message']
        if not fullname or not email or not message:
            errors = 'Please Enter all the fields'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors = 'Your email is invalid. It should look like example@ex.com'
        if not errors:
            connection = sqlite3.connect('booking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("insert into contact (fullname, email, message) values (?, ?, ?)", (fullname, email, message))
            connection.commit()
            return render_template("contact.html")
        else:
            return render_template("contact.html", errors = errors)
    return render_template("contact.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    errors = ''
    successMsg = ''
    print(f'in signup : {request.method}')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email or not password:
            errors = 'Please Enter all the fields'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors = 'Your email is invalid. It should look like example@ex.com'
        elif len(password) <= 4:
            errors = 'YOur password must contain at least 5 characters.'
        if not errors:
            connection = sqlite3.connect('booking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("select * from users where email = ? and password = ? ", (email, password))
            user = executing_cursor.fetchone()
            if user:
                successMsg = 'Logged in successfully.'
                return render_template("index.html")
            else :
                errors = 'Invalid login credentials'
    return render_template("login.html", errors = errors, successMsg = successMsg)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    errors = ''
    successMsg = ''
    print(f'in signup : {request.method}')
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        conf_pass = request.form['conf_pass']
        if not fname or not lname or not username or not email or not password or not conf_pass:
            errors = 'Please Enter all the fields'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            errors = 'Your email is invalid. It should look like example@ex.com'
        elif not password == conf_pass:
            errors = "Both password and Confirmation password must be same."
        elif len(password) <= 4:
            errors = 'YOur password must contain at least 5 characters.'
        if not errors:
            connection = sqlite3.connect('booking.db')
            executing_cursor = connection.cursor()
            executing_cursor.execute("select * from users where email = ? and password = ? ", (email, password))
            toBeCreateduser = executing_cursor.fetchone()
            if not toBeCreateduser:
                executing_cursor.execute("insert into users (fname, lname, email, username, password) values (?, ?, ?, ?, ?)", (fname, lname, email, username, password))
                connection.commit()
                successMsg = 'Your account has been created successfully.'
                return render_template("index.html")
            else :
                errors = 'Looks like you already have an account with us.'
    return render_template("signup.html", errors = errors, successMsg = successMsg)

@app.route('/bookingslist')
def bookingslist():
    con = sqlite3.connect("booking.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM Bookings")

    rows = cur.fetchall();
    return render_template("bookingslist.html", rows=rows)


@app.route('/userslist')
def userslist():
    con = sqlite3.connect("booking.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM users")

    rows = cur.fetchall();
    return render_template("userslist.html", rows=rows)

@app.route('/requestlist')
def requestlist():
    con = sqlite3.connect("booking.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM Contact")

    rows = cur.fetchall();
    return render_template("requestlist.html", rows=rows)
