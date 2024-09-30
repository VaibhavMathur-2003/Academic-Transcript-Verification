import sqlite3
from flask import Flask, render_template, request, send_file, g, jsonify, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from function import process_html
from flask_cors import cross_origin
import io
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

DATABASE = 'criteria.db'

def process_csv(file):
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.reader(stream)
    next(csv_reader)  # Skip the header row
    db = get_db()
    cursor = db.cursor()
    for row in csv_reader:
        course, course_title, credits, reg_type, elective_type = row
        cursor.execute('INSERT INTO courses (course, course_title, credits, reg_type, elective_type) VALUES (?, ?, ?, ?, ?)',
                       (course, course_title, credits, reg_type, elective_type))
    db.commit()
    
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            report_data = process_html(file)
            return render_template('report.html', report_data=report_data)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['admin'] = True
            return redirect(url_for('admin'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone() is not None:
            flash('Username already exists')
        else:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
            flash('Successfully signed up! Please log in.')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.csv'):
                process_csv(file)
                flash('Courses added successfully from CSV!')
            else:
                flash('Please upload a CSV file.')
        else:
            course = request.form['course']
            course_title = request.form['course_title']
            credits = request.form['credits']
            reg_type = request.form['reg_type']
            elective_type = request.form['elective_type']
            
            db = get_db()
            db.execute('INSERT INTO courses (course, course_title, credits, reg_type, elective_type) VALUES (?, ?, ?, ?, ?)',
                       (course, course_title, credits, reg_type, elective_type))
            db.commit()
            flash('Course added successfully!')
        
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(host="0.0.0.0", port=5000, debug=True)