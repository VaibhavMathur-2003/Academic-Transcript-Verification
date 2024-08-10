from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import csv
<<<<<<< HEAD
import io
from function import process_html
=======
from io import BytesIO, StringIO
from flask_cors import CORS  # Import CORS
>>>>>>> b888fe5a1e0d252d2cce0c85141e737df82f47a2

app = Flask(__name__)
CORS(app) 

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