import os
import sqlite3
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Use /tmp folder on Render, local directory otherwise
if os.environ.get('RENDER'):
    DB_FILE = os.path.join('/tmp', 'students.db')
else:
    DB_FILE = 'students.db'

def init_db():
    # Ensure the folder exists (usually not needed for root, but just in case)
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True) if os.path.dirname(DB_FILE) else None

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json
    name = data.get('name')
    subject = data.get('subject')
    score = data.get('score')

    if not name or not subject or not score:
        return jsonify({'error': 'Missing fields'}), 400

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('INSERT INTO students (name, subject, score) VALUES (?, ?, ?)', (name, subject, score))
        conn.commit()
    return jsonify({'status': 'success'})

@app.route('/data')
def get_data():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT name, subject, score FROM students')
        rows = cursor.fetchall()

    students = {}
    for name, subject, score in rows:
        if name not in students:
            students[name] = {}
        students[name][subject] = score

    result = [{'name': name, 'scores': scores} for name, scores in students.items()]
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
