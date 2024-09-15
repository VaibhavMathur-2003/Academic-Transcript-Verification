from flask import send_file
from bs4 import BeautifulSoup
import csv
from io import BytesIO, StringIO

def process_html(file):
    soup = BeautifulSoup(file, 'html.parser')
    data = []
    grade_points = {'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C+': 6, 'C': 5, 'D': 4, 'F': 0}

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
            
            # Add col8
            col8 = li.find('span', class_='col8')
            col8_text = col8.text.strip() if col8 else ''
            row.append(col8_text)
            
            try:
                credits = float(row[2])  # col3 contains credits
                if col8_text and col8_text != 'P':
                    grade = grade_points.get(col8_text, 0)
                    ul_total_points += credits * grade
                    ul_total_credits += credits
            except ValueError:
                print("Error")

            data.append(row)

        if ul_total_credits > 0:
            ul_average = ul_total_points / ul_total_credits
            print(f"Average for {header}: {ul_average:.2f}")
        else:
            print(f"No valid grades for {header}")

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Course', 'Course Title', 'Credits', 'Reg. Type', 'Elective Type', 'Grade'])
    writer.writerows(data)

    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()

    return send_file(
        mem,
        as_attachment=True,
        download_name='output.csv',
        mimetype='text/csv'
    )