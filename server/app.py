from flask import Flask, request, jsonify, send_file, render_template
from bs4 import BeautifulSoup
import csv
from io import BytesIO, StringIO
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app) 

def grade_to_number(grade):
    grade_map = {
        'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C+': 6, 'C': 5, 'D': 4, 'F': 0
    }
    return grade_map.get(grade, 0)

def extract_html_to_csv(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Using StringIO to write CSV data first as strings
    string_output = StringIO()
    writer = csv.writer(string_output)
    writer.writerow(['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'Weighted Score', 'Average'])

    uls = soup.find_all('ul', class_='subCnt')

    for ul in uls:
        lis = ul.find_all('li', class_='dataLi')
        total_weighted_score = 0
        total_credits = 0

        for li in lis:
            row = [span.get_text(strip=True) for span in li.find_all('span', class_='col')]
            if row:
                row = row + [''] * (6 - len(row))
                if row[5] == 'P':
                    writer.writerow(row + ['N/A', 'Not included in average'])
                    continue

                credits = float(row[2]) if row[2] and row[2].replace('.', '').isdigit() else 0
                grade = row[5] if row[5] else ''
                grade_value = grade_to_number(grade)
                weighted_score = credits * grade_value
                total_weighted_score += weighted_score
                total_credits += credits

                row.append(weighted_score)
                writer.writerow(row)

        if total_credits > 0:
            average = total_weighted_score / total_credits
        else:
            average = 0

        writer.writerow(['Average for this ul', '', '', '', '', '', '', f'{average:.2f}'])
        writer.writerow([])

    # Convert StringIO content to bytes and write to BytesIO
    byte_output = BytesIO()
    byte_output.write(string_output.getvalue().encode('utf-8'))
    byte_output.seek(0)

    return byte_output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        html_content = file.read().decode('utf-8')
        csv_output = extract_html_to_csv(html_content)
        csv_filename = 'output_with_average.csv'

        return send_file(csv_output, mimetype='text/csv', as_attachment=True, download_name=csv_filename)

if __name__ == '__main__':
    app.run(debug=True)
