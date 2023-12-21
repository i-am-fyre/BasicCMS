from flask import Flask, render_template, request, redirect, url_for, session
import configparser
import MySQLdb
import re
from secrets import token_hex
from hashlib import sha1
import datetime
import csv

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')

app.secret_key = token_hex(16)

# Initialize database
db = MySQLdb.connect(host=config.get('Database', 'host'),
                        user=config.get('Database', 'user'),
                        password=config.get('Database', 'password'),
                        port=int(config.get('Database', 'port')))

realmd_db = config.get('RealmDatabase', 'realmd')

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
        cur = db.cursor(MySQLdb.cursors.DictCursor)

        # Get user by username
        result = cur.execute("SELECT * FROM " + realmd_db + ".account WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['sha_pass_hash']
            

            # Compare Passwords
            if sha1((username + ":" + password_candidate).upper().encode('utf-8')).hexdigest().upper() == password.upper():
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['gmlevel'] = data['gmlevel']
                session['account_id'] = data['id']

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

        cur = db.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM ' + realmd_db + '.account WHERE username = %s', (username,))
        account = cur.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not expansion:
            msg = 'Please fill out the form!'
        else:
            sha_pass_hash = sha1((username + ":" + password).upper().encode('utf-8')).hexdigest()
            cur.execute('INSERT INTO ' + realmd_db + '.account (username, sha_pass_hash, expansion) VALUES (%s, %s, %s)', (username, sha_pass_hash, expansion))
            db.commit()
            msg = 'You have successfully registered!'
            
        # Close connection
        cur.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    cur = db.cursor(MySQLdb.cursors.DictCursor)

    characters = []
    guilds = []
    guild_members = []
    guild_ranks = []
    character_dbs = config.items( "CharacterDatabases" )
    for key, char_db in character_dbs:
        cur.execute('SELECT * FROM ' + char_db + '.characters WHERE account = %s', (session['account_id'],))
        chars = cur.fetchall()
        characters.append(chars)

        cur.execute('SELECT * FROM ' + char_db + '.guild')
        g = cur.fetchall()
        guilds.append(g)

        cur.execute('SELECT * FROM ' + char_db + '.guild_member WHERE guid IN (SELECT guid FROM ' + char_db + '.characters WHERE account = %s)', (session['account_id'],))
        gm = cur.fetchall()
        guild_members.append(gm)

        cur.execute('SELECT * FROM ' + char_db + '.guild_rank')
        gr = cur.fetchall()
        guild_ranks.append(gr)

    cur.execute('SELECT * FROM ' + realmd_db + '.realmlist')
    realms = cur.fetchall()
    cur.execute('SELECT * FROM ' + realmd_db + '.account')
    accounts = cur.fetchall()

    # Close connection
    cur.close()

    return render_template('profile.html', msg='', characters=characters, realms=realms, accounts=accounts, guilds=guilds, guild_members=guild_members, guild_ranks=guild_ranks)

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    return render_template('admin_dashboard.html', msg='')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    old_password = request.form['old_password']
    new_password = request.form['new_password']

    if old_password and new_password:
        cur = db.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM ' + realmd_db + '.account WHERE username = %s', (session['username'],))
        account = cur.fetchone()

        if account:
            if sha1((session['username'] + ":" + old_password).upper().encode('utf-8')).hexdigest().upper() == account['sha_pass_hash'].upper():
                sha_pass_hash = sha1((session['username'] + ":" + new_password).upper().encode('utf-8')).hexdigest().upper()
                cur.execute('UPDATE ' + realmd_db + '.account SET sha_pass_hash = %s, v = %s, s = %s WHERE username = %s', (sha_pass_hash, "", "", session['username']))
                db.commit()
                msg = 'Password successfully changed!'
            else:
                msg = 'Old password is incorrect!'
        else:
            msg = 'Account not found!'

        # Close connection
        cur.close()

    return render_template('profile.html', msg='')

@app.template_filter('convert_date')
def format_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@app.template_filter('convert_time')
def format_time(seconds):
    return datetime.timedelta(seconds=seconds)

@app.template_filter('zone_name')
def zone_name(zone_id):
    with open('data/AreaTable.dbc.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader: 
            if int(row[0]) == int(zone_id):
                return row[13]
