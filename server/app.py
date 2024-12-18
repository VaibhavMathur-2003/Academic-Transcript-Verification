import sqlite3
from flask import Flask, render_template, request, send_file, g, jsonify, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from function import process_html
from flask_cors import cross_origin
import io
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

DATABASE = 'criteria.db'

def process_csv(file):
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.reader(stream)
    next(csv_reader)
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



@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file:
            report_data = process_html(file)
            return jsonify(report_data)
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

@app.route('/courses')
def view_courses():
    db = get_db()
    branches = db.execute('SELECT DISTINCT branch FROM courses').fetchall()
    
    branch_filter = request.args.get('branch', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'course')  
    
    query = 'SELECT * FROM courses WHERE 1=1'
    params = []
    
    if branch_filter:
        query += ' AND branch = ?'
        params.append(branch_filter)
    if search_query:
        query += ' AND (course LIKE ? OR course_title LIKE ?)'
        params.extend(['%' + search_query + '%'] * 2)
    
    query += f' ORDER BY {sort_by}'
    courses = db.execute(query, params).fetchall()
    
    return render_template('courses.html', 
                         courses=courses, 
                         branches=branches,
                         current_branch=branch_filter,
                         search_query=search_query,
                         sort_by=sort_by)

@app.route('/courses/add_version/<int:original_course_id>', methods=['GET', 'POST'])
@login_required 
def add_course_version(original_course_id):
    db = get_db()
    original_course = db.execute('SELECT * FROM courses WHERE id = ?', [original_course_id]).fetchone()
    
    if request.method == 'POST':
        course = request.form['course']
        course_title = request.form['course_title']
        credits = request.form['credits']
        reg_type = request.form['reg_type']
        elective_type = request.form['elective_type']
        branch = request.form['branch']
        
        max_version = db.execute('''
            SELECT COALESCE(MAX(version), 0) + 1 as new_version 
            FROM courses 
            WHERE course = ? AND branch = ?
        ''', (original_course['course'], original_course['branch'])).fetchone()['new_version']
        
        db.execute('''
            UPDATE courses 
            SET is_current = 0 
            WHERE course = ? AND branch = ?
        ''', (original_course['course'], original_course['branch']))
        
        db.execute('''
            INSERT INTO courses 
            (course, course_title, credits, reg_type, elective_type, branch, 
            version, parent_course_id, is_current)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            course, course_title, credits, reg_type, 
            elective_type, branch, max_version, original_course_id
        ))
        db.commit()
        
        flash('New course version added successfully!')
        return redirect(url_for('view_courses'))
    
    return render_template('edit_course.html', course=original_course, is_version=True)

@app.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required 
def edit_course(id):
    db = get_db()
    if request.method == 'POST':
        course = request.form['course']
        course_title = request.form['course_title']
        credits = request.form['credits']
        reg_type = request.form['reg_type']
        elective_type = request.form['elective_type']
        branch = request.form['branch']
        
        db.execute('''UPDATE courses 
                     SET course = ?, course_title = ?, credits = ?, 
                         reg_type = ?, elective_type = ?, branch = ?
                     WHERE id = ?''',
                  (course, course_title, credits, reg_type, 
                   elective_type, branch, id))
        db.commit()
        flash('Course updated successfully!')
        return redirect(url_for('view_courses'))
    
    course = db.execute('SELECT * FROM courses WHERE id = ?', 
                       [id]).fetchone()
    if course is None:
        flash('Course not found!')
        return redirect(url_for('view_courses'))
    
    return render_template('edit_course.html', course=course)

@app.route('/courses/delete/<int:id>', methods=['POST'])
@login_required 
def delete_course(id):
    db = get_db()
    db.execute('DELETE FROM courses WHERE id = ?', [id])
    db.commit()
    flash('Course deleted successfully!')
    return redirect(url_for('view_courses'))

from werkzeug.utils import secure_filename
import os
from adminfunction import process_transcript  

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import Flask, request, flash, redirect, stream_with_context, Response
from werkzeug.utils import secure_filename
import os
from werkzeug.exceptions import RequestEntityTooLarge

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 100 
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['CHUNK_SIZE'] = 4096 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

@app.route('/transcript', methods=['GET', 'POST'])
def process_transcript_route():
    if request.method == 'POST':
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
            
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            try:
                with open(filepath, 'wb') as f:
                    while True:
                        chunk = file.stream.read(app.config['CHUNK_SIZE'])
                        if not chunk:
                            break
                        f.write(chunk)
                
                try:
                    results = process_transcript(filepath, 
                        os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_data.json'))
                    
                    db = get_db()
                    
                    processed_results = []
                    for student in results:
                        student_branch = student['Branch']
                        
                        db_courses = db.execute(
                            'SELECT * FROM courses WHERE branch = ?', 
                            (student_branch,)
                        ).fetchall()
                        
                        student_courses = {
                            course['Course No']: course 
                            for course in student['Courses']
                        }
                        
                        
                        parent_child_map = {}
                        for db_course in db_courses:
                            parent_id = db_course['parent_course_id']
                            course_no = db_course['course']
                            
                            if parent_id:
                                parent_course = db.execute(
                                    'SELECT course FROM courses WHERE id = ?', 
                                    (parent_id,)
                                ).fetchone()
                                
                                if parent_course:
                                    parent_course_code = parent_course['course']
                                    if parent_course_code not in parent_child_map:
                                        parent_child_map[parent_course_code] = set()
                                    parent_child_map[parent_course_code].add(course_no)
                        
                        
                        missing_courses = []
                        for db_course in db_courses:
                            course_no = db_course['course']
                            
                            is_course_present = course_no in student_courses
                            
                            is_parent_version_present = any(
                                parent in student_courses 
                                for parent in parent_child_map.keys() 
                                if course_no in parent_child_map.get(parent, set())
                            )
                            
                            is_child_version_present = any(
                                child in student_courses 
                                for child in parent_child_map.get(course_no, set())
                            )
                            
                            if not (is_course_present or is_parent_version_present or is_child_version_present):
                                missing_courses.append({
                                    'course': db_course['course'],
                                    'course_title': db_course['course_title'],
                                    'credits': db_course['credits'],
                                    'reg_type': db_course['reg_type'],
                                    'elective_type': db_course['elective_type'],
                                    'version': db_course['version'],
                                    'parent_course_id': db_course['parent_course_id']
                                })
                        
                        student['missing_courses'] = missing_courses
                        processed_results.append(student)
                    
                    os.remove(filepath)
                    
                    return stream_with_context(
                        render_template(
                            'transcript_results.html',
                            students=processed_results
                        )
                    )
                    
                except Exception as process_error:
                    import traceback
                    traceback.print_exc()
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

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum size is 100MB.')
    return redirect(url_for('process_transcript_route')), 413

@app.route('/upload-progress')
def upload_progress():
    progress = session.get('upload_progress', 0)
    return jsonify({'progress': progress})


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)