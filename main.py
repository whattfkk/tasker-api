from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
import config
import sqlite3

app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username and password:
        connection = sqlite3.connect(config.usersdb)
        cursor = connection.cursor()

        cursor.execute('SELECT username, password FROM Users WHERE username = ?', (username,))
        
        results = cursor.fetchall()
        if username == results[0][0] and password == results[0][1]:
            connection.close()
            return username
        else:
            connection.close()
            return 'login or password are incorrect'

@app.route('/', methods=['GET'])
def hello():
    return {"success": "true"}

@app.route('/create_account', methods=['POST'])
def create_account():
    input_json = request.get_json(force = True)
    login = input_json['login']
    password = input_json['password']
    connection = sqlite3.connect(config.usersdb)
    cursor = connection.cursor()

    cursor.execute('SELECT username FROM Users WHERE username = ?', (login,))
    results = cursor.fetchall()
    if results:
        return 'This username already registered.'
    elif not results:
        cursor.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (login, password))
        connection.commit()
        connection.close()
        return {"success": "true", "login": login, "password": password}

@app.route('/login', methods=['POST'])
def login():
    input_json = request.get_json(force = True)
    login = input_json['login']
    password = input_json['password']
    connection = sqlite3.connect(config.usersbd)
    cursor = connection.cursor()

    cursor.execute('SELECT id, username, password FROM Users WHERE username = ?', (login,))
    results = cursor.fetchall()
    print(results)
    if results:
        print(results)
        if login == results[0][1] and password_hash == results[0][2]:
            return {"success": "true", "username": login, "id": results[0][0]}
    elif not results:
        return {"success": "false", "cause": "login or password incorrect."}
    connection.close()

@app.route('/create_task', methods=['POST'])
@auth.login_required
def create_task():
    input_json = request.get_json(force = True)
    text = input_json['text']
    connection = sqlite3.connect(config.tasksdb)
    cursor = connection.cursor()
    now = datetime.now()
    cursor.execute('INSERT INTO Notes (username, text, timestamp, is_done) VALUES (?, ?, ?, ?)', (auth.current_user(), text, now, 'false'))
    connection.commit()
    cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE username = ? and timestamp = ?', (auth.current_user(), now,))
    results = cursor.fetchall()
    connection.close()
    return {"success": "true", "text": results[0][2], "username": results[0][1], "timestamp": results[0][3], "is_done": results[0][4]}

@app.route('/edit_task/<string:task_id>', methods=['PUT'])
@auth.login_required
def edit_task(task_id):
    input_json = request.get_json(force = True)
    new_text = input_json['text']
    connection = sqlite3.connect(config.tasksdb)
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
        results = cursor.fetchall()
        if auth.current_user() == results[0][1]:
            cursor.execute('UPDATE Notes SET text = ? WHERE id = ?', (new_text, task_id))
            connection.commit()
            cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
            results1 = cursor.fetchall()
            return {"success": "true", "id": results1[0][0], "username": results1[0][1], "text": results1[0][2], "timestamp": results1[0][3], "is_done": results1[0][4]}
        else:
            connection.close()
            return {"success": "false"}
    except IndexError:
        return {"success": "false", "cause": "task not exist"}
    
@app.route('/delete_task/<string:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
    connection = sqlite3.connect(config.tasksdb)
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
        results = cursor.fetchall()
        if auth.current_user() == results[0][1]:
            cursor.execute('DELETE FROM Notes WHERE id = ?', (task_id,))
            connection.commit()
            return {"success": "true"}
        else:
            connection.close()
            return {"success": "false"}
    except IndexError:
        return {"success": "false", "cause": "task not exist"}

@app.route('/get_tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    connection = sqlite3.connect(config.tasksdb)
    cursor = connection.cursor()
    cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE username = ?', (auth.current_user(),))
    results = cursor.fetchall()
    amount = []
    for i in results:
        temp = {}
        temp['id'] = i[0]
        temp['username'] = i[1]
        temp['text'] = i[2]
        temp['timestamp'] = i[3]
        temp['is_done'] = i[4]
        amount.append(temp)
    return amount

@app.route('/get_task/<string:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
    connection = sqlite3.connect(config.tasksdb)
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
        results = cursor.fetchall()
        if auth.current_user() == results[0][1]:
            connection.close()
            return {"success": "true", "id": results[0][0], "username": results[0][1], "text": results[0][2], "timestamp": results[0][3], "is_done": results[0][4]}
        else:
            connection.close()
            return {"success": "false"}
    except IndexError:
        return {"success": "false", "cause": "task not exist"}

@app.route('/task_done/<string:task_id>', methods=['PUT'])
@auth.login_required
def task_done(task_id):
    connection = sqlite3.connect(config.tasksdb)
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
        results = cursor.fetchall()
        print(auth.current_user())
        print(results)
        print(results[0][1])
        if auth.current_user() == results[0][1]:
            if results[0][4] == 'false':
                cursor.execute('UPDATE Notes SET is_done = ? WHERE id = ?', ('true', task_id))
                connection.commit()
                cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
                results1 = cursor.fetchall()
                return {"success": "true", "id": results1[0][0], "username": results1[0][1], "text": results1[0][2], "timestamp": results1[0][3], "is_done": results1[0][4]}
            elif results[0][4] == 'true':
                cursor.execute('UPDATE Notes SET is_done = ? WHERE id = ?', ('false', task_id))
                connection.commit()
                cursor.execute('SELECT id, username, text, timestamp, is_done FROM Notes WHERE id = ?', (task_id,))
                results1 = cursor.fetchall()
                return {"success": "true", "id": results1[0][0], "username": results1[0][1], "text": results1[0][2], "timestamp": results1[0][3], "is_done": results1[0][4]}
        else:
            connection.close()
            return {"success": "false"}
    except IndexError:
        return {"success": "false", "cause": "task not exist"}

if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=5050)