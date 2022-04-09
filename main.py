from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from secrets import token_hex
from hashlib import sha1

app = Flask(__name__)

app.secret_key = token_hex(16)

# Enter your database connnection details
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'mangos'
app.config['MYSQL_PASSWORD'] = 'mangos'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'realmd'

# Initialize database
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ''
    return render_template('index.html', msg='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'expansion' in request.form:
        username = request.form['username']
        password = request.form['password']
        expansion = request.form['expansion']

        print (expansion)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not expansion:
            msg = 'Please fill out the form!'
        else:
            pre_hash_pass = (username + ":" + password).upper()
            sha_pass_hash = sha1(pre_hash_pass.encode('utf-8')).hexdigest()
            cursor.execute('INSERT INTO account (username, sha_pass_hash, expansion) VALUES (%s, %s, %s)', (username, sha_pass_hash, expansion))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('index.html', msg=msg)