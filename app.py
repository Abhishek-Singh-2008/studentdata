from flask import Flask, request, jsonify, send_file, redirect
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'students.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL
            );
        ''')

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/data')
def data():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute('SELECT name, subject, score FROM students')
        rows = cur.fetchall()
 
    student_dict = {}
    for name, subject, score in rows:
        if name not in student_dict:
            student_dict[name] = {}
        student_dict[name][subject] = score

    students = [{'name': name, 'scores': scores} for name, scores in student_dict.items()]
    return jsonify(students)

@app.route('/submitdata', methods=['POST'])
def submit_data():
    data = request.json
    name = data.get('name')
    scores = data.get('scores', {})

    with sqlite3.connect(DB_FILE) as conn:
        for subject, score in scores.items():
            if isinstance(score, int):
                conn.execute(
                    'INSERT INTO students (name, subject, score) VALUES (?, ?, ?)',
                    (name, subject, score)
                )
    return jsonify({"message": "Data added successfully"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
