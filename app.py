import re
import requests
from flask import (Flask,
                    render_template,
                    request,
                    redirect,
                    session,
                    json,
                    jsonify)
from flask.helpers import url_for
import sqlite3

app = Flask(__name__)

app.secret_key = 'super secret key'

admin_username, admin_password, admin_credentials = 'admin', 'admin', 'admin'
accounts = {'admin': {'password': 'admin', 'credentials': 'doctor'},
            'patient': {'password': 'patient', 'credentials': 'patient'},
            'doctor': {'password': 'doctor', 'credentials': 'doctor'}}


@app.route('/', methods=['GET', 'POST'])
def main():
    session.clear()
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        response = requests.post("http://localhost:5000/login", json = {'username': username,
                                                                        'password': password})
        if response.json()['status'] == 'ok':
            session['credentials'] = response.json()['credential']
            session['username'] = username
            return redirect(url_for('start', username = username))                  
        else:
            pass
    return render_template('login.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    try:
        username = request.json['username']
        password_from_user = request.json['password']
        if username == 'admin' and password_from_user == 'admin':
            return jsonify({'status': 'ok', 
                    'credential': 'doctor'})
        conn = sqlite3.connect('databases/database.db')
        c = conn.cursor()  
        password_from_db = c.execute(f'SELECT password FROM persons WHERE pesel = \'{username}\'')
        for password_elem in password_from_db.fetchone():
            if password_elem == password_from_user:
                credentials_for_user = c.execute(f'SELECT credentials FROM persons WHERE pesel = \'{username}\'')
                for credential_elem in credentials_for_user.fetchone():
                    conn.close()             
                    return jsonify({'status': 'ok', 
                                    'credential': credential_elem})
            else:
                conn.close() 
                return jsonify({'status': 'nok'})
    except:
        return jsonify({'status': 'nok'})


@app.route('/start')
def start():
    if not session['username']:
        return redirect(url_for('main'))
    credentials = session['credentials']
    username = session['username']
    if credentials == 'patient':
        return render_template('patient/start.html', username = username, credentials = credentials)
    elif credentials == 'doctor':
      return render_template('doctor/start.html', username = username, credentials = credentials)
    else:
        return redirect(url_for('main'))


@app.route('/add_patients_doctors', methods=['POST', 'GET'])
def add_patients_doctors():
    if session['username'] and session['credentials'] != 'doctor':
        return redirect(url_for('main'))
    
    if request.method == "POST":
        name = request.form['name']
        surname = request.form['surname']
        pesel = request.form['pesel']
        city = request.form['city']
        street = request.form['street']
        phone_number = request.form['phone_number']
        credential = request.form['credential']
        if credential == "Pacjent":
            credential = 'patient'
        elif credential == "Lekarz":
            credential = 'doctor'
        response = requests.post("http://localhost:5000/add_user", json = {"name": name,
                                                    "surname": surname,
                                                    "pesel": pesel,
                                                    "city": city,
                                                    "street": street,
                                                    "phone_number": phone_number,
                                                    "credential": credential})
        if response.json()['status'] == 'ok':
            print(response.json())

    return render_template('doctor/add_patients_doctors.html', username = session['username'])

@app.route('/add_user', methods = ['GET', 'POST'])
def add_user():
    try:
        name = request.json['name']
        surname = request.json['surname']
        pesel = request.json['pesel']
        city = request.json['city']
        street = request.json['street']
        phone_number = request.json['phone_number']
        credential = request.json['credential']
        conn = sqlite3.connect('databases/database.db')
        c = conn.cursor()
        c.execute(f'INSERT INTO persons VALUES (\'{name}\', \'{surname}\', {pesel}, \'{city}\', \'{street}\', \'{phone_number}\', \'{credential}\', \'zmienhaslo1\')')
        conn.commit()
        conn.close()
        
        file = open('text.txt', 'a')
        file.write(str(request.json))
        return jsonify({'status': 'ok'})
    except:
        return jsonify({'status': 'nok'})

@app.route('/patients_list', methods=['POST', 'GET'])
def patients_list():
    list = []
    conn = sqlite3.connect('databases/database.db')
    c = conn.cursor()
    user_list = c.execute(f'SELECT name, surname, pesel, city, street, phone_number FROM persons')
    for row in user_list.fetchall():
        list.append(row)
    return render_template('doctor/patients_list.html', username = session['username'], list=list)
    

@app.route('/user_list', methods = ['GET', 'POST'])
def user_list():
    try:
        list = {}
        i = 1
        conn = sqlite3.connect('databases/database.db')
        c = conn.cursor()
        user_list = c.execute(f'SELECT name, surname, pesel, city, street, phone_number FROM persons')
        for row in user_list.fetchall():
            list[i] = row
            i += 1
        return jsonify({'status': 'ok', 'list': list})
    except:
        return jsonify({'status': 'nok'})


