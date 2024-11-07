import re
import json
import cv2
import pytesseract
import numpy as np
from pdf2image import convert_from_path
from difflib import SequenceMatcher
import pdfplumber
from PIL import Image, ImageEnhance, ImageFilter


# sudo apt-get update
# sudo apt-get install tesseract-ocr
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
# pytesseract.pytesseract.tesseract_cmd = r'c:/Program Files/Tesseract-OCR/tesseract.exe'

def similarity_ratio(str1, str2):
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def standardize_name(name):
    return ' '.join(name.upper().split())

def find_similar_name_group(name, existing_groups, similarity_threshold=0.85):
    name = standardize_name(name)

    for group_name, variations in existing_groups.items():
        if similarity_ratio(name, group_name) > similarity_threshold:
            return group_name
        for variation in variations:
            if similarity_ratio(name, variation) > similarity_threshold:
                return group_name
    return None

def is_valid_course(course_no, course_title, grade):
    if len(course_no) < 4 or not any(c.isdigit() for c in course_no):
        return False

    course_title = course_title.replace(" ", "")
    if len(course_title) < 5:
        return False

    letter_ratio = sum(c.isalpha() for c in course_title) / len(course_title)
    if letter_ratio < 0.7:
        return False

    valid_grades = {'A', 'B', 'C', 'D', 'E', 'F', 'P', 'G'}
    base_grade = grade[0].upper()
    if base_grade not in valid_grades:
        return False

    invalid_words = {'signature', 'seal', 'transcript', 'authority', 'principal', 'registrar'}
    if any(word.lower() in course_title.lower() for word in invalid_words):
        return False

    return True

def merge_student_records(students_list):
    name_groups = {}
    merged_students = {}

    for student in students_list:
        name = student["Name"]
        std_name = standardize_name(name)

        group_name = find_similar_name_group(std_name, name_groups)

        if group_name is None:
            name_groups[std_name] = {name}
            group_name = std_name
        else:
            name_groups[group_name].add(name)

        if group_name not in merged_students:
            merged_students[group_name] = student.copy()
        else:
            existing_courses = {(c["Course No"], c["Course Title"])
                              for c in merged_students[group_name]["Courses"]}

            for course in student["Courses"]:
                course_key = (course["Course No"], course["Course Title"])
                if course_key not in existing_courses:
                    merged_students[group_name]["Courses"].append(course)

    result = list(merged_students.values())

    for student in result:
        std_name = standardize_name(student["Name"])
        if std_name in name_groups:
            student["name_variations"] = list(name_groups[std_name])

    return result


def preprocess_image_for_ocr(image):

    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    sharpened_image = cv2.filter2D(blurred_image, -1, kernel)

    pil_image = Image.fromarray(sharpened_image)
    enhancer = ImageEnhance.Contrast(pil_image)
    enhanced_image = enhancer.enhance(2)

    return enhanced_image

def extract_text_with_ocr(page):

    img = page.to_image(resolution=300).original
    preprocessed_img = preprocess_image_for_ocr(img)

    ocr_text = pytesseract.image_to_string(preprocessed_img, lang='eng', config='--psm 6')
    return ocr_text


def extract_text_from_pdf(pdf_path):
    all_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()

            if text:
                all_text += f"\n--- Page {page_num + 1} ---\n" + text
            else:
                print(f"Using OCR for page {page_num + 1}")
                ocr_text = extract_text_with_ocr(page)
                all_text += f"\n--- Page {page_num + 1} (OCR) ---\n" + ocr_text

    return all_text


def split_into_student_records(text):
    records = text.split("GRADE REPORT")
    return [record.strip() for record in records if record.strip()]

def convert_transcript_to_json(text):
    student_records = split_into_student_records(text)
    all_students = []

    for record in student_records:
        name_match = re.search(r'Name\s*:\s*([^\n]+)', record)
        branch_match = re.search(r'Degree\s*:\s*([^\n]+)', record)
        if not name_match:
            continue

        name = name_match.group(1).strip()
        branch = branch_match.group(1).strip()
        course_pattern = r'([A-Za-z0-9&]+)\s+([A-Za-z\s&]+(?:\s+[A-Za-z\s&]+)?)\s+(\d+(?:\.\d+)?)\s+([A-Fa-fPpG][+-]?)'
        courses = []

        matches = re.finditer(course_pattern, record)
        for match in matches:
            course_no = match.group(1).strip()
            course_title = match.group(2).strip()
            grade = match.group(4).strip()

            if is_valid_course(course_no, course_title, grade):
                course = {
                    "Course No": course_no.upper(),
                    "Course Title": course_title,
                    "Credits": float(match.group(3)),
                    "Grade": grade.upper()
                }
                courses.append(course)

        student_entry = {
            "Name": name,
            "Branch": branch,
            "Courses": courses
        }
        all_students.append(student_entry)

    return merge_student_records(all_students)

def process_transcript(pdf_path, output_json_path):
    extracted_text = extract_text_from_pdf(pdf_path)
    result = convert_transcript_to_json(extracted_text)

    with open(output_json_path, 'w') as f:
        json.dump(result, indent=2, fp=f)

    return result