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
        branch, course, course_title, credits, reg_type, elective_type = row
        cursor.execute('INSERT INTO courses (branch, course, course_title, credits, reg_type, elective_type) VALUES (?, ?, ?, ?, ?, ?)',
                       (branch, course, course_title, credits, reg_type, elective_type))
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



@app.route('/', methods=['POST'])
@cross_origin()
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        report_data = process_html(file)
        return jsonify(report_data)


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
            branch = request.form['branch']
            course = request.form['course']
            course_title = request.form['course_title']
            credits = request.form['credits']
            reg_type = request.form['reg_type']
            elective_type = request.form['elective_type']
            
            db = get_db()
            db.execute('INSERT INTO courses (branch, course, course_title, credits, reg_type, elective_type) VALUES (?, ?, ?, ?, ?, ?)',
                       (branch, course, course_title, credits, reg_type, elective_type))
            db.commit()
            flash('Course added successfully!')
        
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# First add these imports at the top of your app.py
from werkzeug.utils import secure_filename
import os
from adminfunction import process_transcript  # Assuming you'll save the transcript processing code in function.py

# Add these configurations after app creation
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Update the route in app.py
from flask import Flask, request, flash, redirect, stream_with_context, Response
from werkzeug.utils import secure_filename
import os
from werkzeug.exceptions import RequestEntityTooLarge

# Configuration settings
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 100  # 100MB limit
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['CHUNK_SIZE'] = 4096  # 4KB chunks for streaming

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

@app.route('/transcript', methods=['GET', 'POST'])
def process_transcript_route():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            try:
                # Stream the file to disk in chunks
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = file.stream.read(app.config['CHUNK_SIZE'])
                        if not chunk:
                            break
                        f.write(chunk)
                
                # Process the PDF and get results
                try:
                    results = process_transcript(filepath, 
                        os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_data.json'))
                    
                    # Get database connection
                    db = get_db()
                    
                    # Process results in chunks to avoid memory issues
                    processed_results = []
                    for student in results:
                        student_branch = student['Branch']
                        
                        # Get courses for student's branch
                        db_courses = db.execute(
                            'SELECT * FROM courses WHERE branch = ?', 
                            (student_branch,)
                        ).fetchall()
                        
                        student_courses = {
                            course['Course No']: course 
                            for course in student['Courses']
                        }
                        
                        missing_courses = []
                        for db_course in db_courses:
                            if db_course['course'] not in student_courses:
                                missing_courses.append({
                                    'course': db_course['course'],
                                    'course_title': db_course['course_title'],
                                    'credits': db_course['credits'],
                                    'reg_type': db_course['reg_type'],
                                    'elective_type': db_course['elective_type']
                                })
                        
                        student['missing_courses'] = missing_courses
                        processed_results.append(student)
                    
                    # Clean up uploaded file
                    os.remove(filepath)
                    
                    # Stream the template response
                    return stream_with_context(
                        render_template(
                            'transcript_results.html',
                            students=processed_results
                        )
                    )
                    
                except Exception as process_error:
                    flash(f'Error processing file: {str(process_error)}')
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return redirect(request.url)
                    
            except RequestEntityTooLarge:
                flash('File too large. Maximum size is 100MB.')
                return redirect(request.url)
                
            except Exception as upload_error:
                flash(f'Error uploading file: {str(upload_error)}')
                return redirect(request.url)
                
    return render_template('transcript_upload.html')

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum size is 100MB.')
    return redirect(url_for('process_transcript_route')), 413

# Optional: Add a progress endpoint for large uploads
@app.route('/upload-progress')
def upload_progress():
    # Implement progress tracking logic here
    progress = session.get('upload_progress', 0)
    return jsonify({'progress': progress})


if __name__ == '__main__':
    init_db()  # Initialize the database before running the app
    app.run(host="0.0.0.0", port=5000, debug=True)