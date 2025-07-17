from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import joblib
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            gender TEXT NOT NULL,
            gmail TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

try:
    model = joblib.load("fake_account_detector.pkl")
except FileNotFoundError:
    print("Error: The model 'fake_account_detector.pkl' is not found.")
    exit()

@app.route('/home')
def homepage():
    return render_template('home.html')

@app.route('/')
def home():
    return redirect(url_for('homepage'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        gender = request.form['gender']
        gmail = request.form['gmail']
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO users (firstname, lastname, gender, gmail, username, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (firstname, lastname, gender, gmail, username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='Username already exists.')

    return render_template('register.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        if not all(k in data for k in ["followers", "following", "posts", "verified"]):
            return jsonify({"error": "Missing required fields"}), 400

        features = np.array([
            data["followers"],
            data["following"],
            data["posts"],
            data["verified"]
        ]).reshape(1, -1)

        prediction = model.predict(features)[0]
        result = "Fake Account" if prediction == 1 else "Real Account"

        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
