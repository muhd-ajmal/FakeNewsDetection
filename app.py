from flask import Flask, request, render_template, jsonify, url_for
from fake_news_detect import predict
import sqlite3 as sql
import hashlib
import os
import warnings

app = Flask(__name__)

hash = (lambda pswd: hashlib.sha256(pswd.encode('utf-8')).hexdigest())
check = False
user = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    if check:
        return render_template("home.html", username=user)
    else:
        return render_template("index.html", load=True)

@app.route('/login', methods=["POST"])
def login(): 
    global check
    global user
    uname = request.form["uname"]
    pswd = request.form["pswd"]
    user = uname
    try:
        conn = sql.connect("Files/user_info.db")
        res = conn.execute(f"SELECT PSWD, FNAME FROM USERS WHERE UNAME='{uname}'").fetchone()
        conn.close()
        if hash(pswd) == res[0]:
            check = True
            return jsonify({'success': True, 'redirect': url_for('home')})
        else:
            return "Invalid password!"
    except Exception as ex:
        return f"{ex}"


@app.route('/logout')
def logout():
    global check
    check = False
    return jsonify({'redirect': url_for('home')})
    
    

@app.route('/change_password', methods=['POST'])
def change_password():
    cpswd = request.form["cpswd"]
    npswd = request.form["npswd"]
    try:
        conn = sql.connect("Files/user_info.db")
        res = conn.execute(f"SELECT PSWD FROM USERS WHERE UNAME='{user}'").fetchone()
        if res == hash(cpswd):
            cursor = conn.cursor()
            cursor.execute(f"UPDATE USERS SET PSWD='{hash(npswd)}' where UNAME='{user}'")
            conn.commit()
            return "Paswword changed successfull"
        else:
            return "Incorrect current password"
    except Exception as ex:
        return f"Password updation failed, error: {ex}"
    

@app.route('/register', methods=["POST"])
def register():
    fname = request.form["fname"]
    uname = request.form["uname"]
    pswd = request.form["pswd"]
    try:
        conn = sql.connect("Files/user_info.db")
        cursor = conn.cursor()
        ch = cursor.execute(f"INSERT INTO USERS VALUES ('{fname}','{hash(pswd)}','{uname}')").fetchone()
        conn.commit()
        conn.close()
        print(ch)
        return "User registration successfull"
    except Exception as ex:
        print(f"{ex}")
        return f"User registration failed, {ex}"


@app.route("/analyze", methods=["POST"])
def analyze_text():
    heading = request.form["heading"]  
    content = request.form["content"]
    subject = request.form["subject"]
    data = predict(heading, content, subject)
    return jsonify({
        'class': str(data[0]),
        'label': data[1],
        'prob': str(data[2])
    })

if __name__ == '__main__':
    app.run(debug=True)