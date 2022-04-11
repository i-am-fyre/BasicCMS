from flask import Flask, render_template, request, redirect, url_for, session
import configparser
import MySQLdb
import re
from secrets import token_hex
from hashlib import sha1

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

app.secret_key = token_hex(16)

# Initialize database
mysql = MySQLdb.connect(host=config.get('Database', 'host'),
                        user=config.get('Database', 'user'),
                        password=config.get('Database', 'password'),
                        port=int(config.get('Database', 'port')),
                        database=config.get('Database', 'realmd_name'))

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ''
    return render_template('index.html', msg='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        # cur = mysql.cursor()
        cur = mysql.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM account WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data[2]
            

            # Compare Passwords
            if sha1((username + ":" + password_candidate).upper().encode('utf-8')).hexdigest().upper() == password.upper():
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['gmlevel'] = data[3]

                return redirect(url_for('index'))
            else:
                error = 'Invalid login'
                return render_template('login.html', msg=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', msg=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    [session.pop(key) for key in list(session.keys()) if key != '_flashes']
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'expansion' in request.form:
        username = request.form['username']
        password = request.form['password']
        expansion = request.form['expansion']

        print (expansion)

        cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not expansion:
            msg = 'Please fill out the form!'
        else:
            sha_pass_hash = sha1((username + ":" + password).upper().encode('utf-8')).hexdigest()
            cursor.execute('INSERT INTO account (username, sha_pass_hash, expansion) VALUES (%s, %s, %s)', (username, sha_pass_hash, expansion))
            mysql.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', msg='')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html', msg='')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    if old_password and new_password:
        cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s', (session['username'],))
        account = cursor.fetchone()

        if account:
            if sha1((session['username'] + ":" + old_password).upper().encode('utf-8')).hexdigest().upper() == account['sha_pass_hash'].upper():
                sha_pass_hash = sha1((session['username'] + ":" + new_password).upper().encode('utf-8')).hexdigest().upper()
                cursor.execute('UPDATE account SET sha_pass_hash = %s, v = %s, s = %s WHERE username = %s', (sha_pass_hash, "", "", session['username']))
                mysql.commit()
                msg = 'Password successfully changed!'
            else:
                msg = 'Old password is incorrect!'
        else:
            msg = 'Account not found!'

    return render_template('profile.html', msg='')