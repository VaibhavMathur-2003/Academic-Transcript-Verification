from flask import send_file, g
from bs4 import BeautifulSoup
import csv
from io import BytesIO, StringIO
import sqlite3

# Define the elective types to be filtered
electives = ["Institute Core Theory", "Open Elective", "Project", "Institute Core Lab", "Program Elective", "Program Core Theory + Lab"]

DATABASE = 'criteria.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Fetch courses from the database along with their elective_type
def get_courses_from_db():
    db = get_db()
    courses = db.execute('SELECT course, course_title, elective_type FROM courses').fetchall()
    return {course['course']: {'title': course['course_title'], 'elective_type': course['elective_type']} for course in courses}

def process_html(file):
    soup = BeautifulSoup(file, 'html.parser')
    data = []
    grade_points = {'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C+': 6, 'C': 5, 'D': 4, 'F': 0}

    db_courses = get_courses_from_db()

    html_courses = set()
    elective_credits = {elective: 0 for elective in electives}
    section_averages = {}

    for ul in soup.find_all('ul', class_='subCnt'):
        header_span = ul.find('span', class_='changeHdrCls')
        sub_header_span = ul.find('span', class_='changeSubHdrCls')

        if header_span and sub_header_span:
            header = header_span.text.strip()
            sub_header = sub_header_span.text.strip()
        else:
            header = "Unknown"

        ul_total_points = 0
        ul_total_credits = 0

        for li in ul.find_all('li', class_='hierarchyLi dataLi tab_body_bg'):
            row = []
            for i in range(1, 6):  # col1 to col5
                col = li.find('span', class_=f'col{i}')
                row.append(col.text.strip() if col else '')

            col8 = li.find('span', class_='col8')
            col8_text = col8.text.strip() if col8 else ''
            row.append(col8_text)

            course_code = row[0]
            electiveTypes = row[4]
            html_courses.add(course_code)

            try:
                credits = float(row[2])
                if electiveTypes in electives:
                    elective_credits[electiveTypes] += credits                    
                if col8_text and col8_text != 'P':
                    grade = grade_points.get(col8_text, 0)
                    ul_total_points += credits * grade
                    ul_total_credits += credits
            except ValueError:
                print(f"Error processing credits for course: {course_code}")

            data.append(row)

        if ul_total_credits > 0:
            ul_average = ul_total_points / ul_total_credits
            section_averages[header] = round(ul_average, 2)

    missing_courses = {
        course_code: course_info
        for course_code, course_info in db_courses.items()
        if course_code not in html_courses and course_info['elective_type'] in electives
    }

    report_data = {
        'elective_credits': elective_credits,
        'section_averages': section_averages,
        'missing_courses': missing_courses,
        'courses': data
    }

    return report_data