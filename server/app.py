from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import csv
import io
from function import process_html

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            return process_html(file)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)