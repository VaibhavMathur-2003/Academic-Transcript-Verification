# Academic Transcript Verification

This application provides a system for verifying academic transcripts. Follow the installation steps below to get started.

## Prerequisites

Before running the application, ensure you have the following installed:
- Git
- Python
- `apt` package manager (for Linux systems)

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/VaibhavMathur-2003/Academic-Transcript-Verification.git
```

2. Navigate to the server directory:
```bash
cd Academic-Transcript-Verification/
cd server
```

3. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Install Tesseract OCR:
```bash
sudo apt-get install tesseract-ocr
```

6. Run the application:
```bash
python app.py
```

7. Access the application:
Once the server is running, open your web browser and navigate to:
```
http://127.0.0.1:5000/transcript
```

## Complete Bash Script:
```bash
git clone https://github.com/VaibhavMathur-2003/Academic-Transcript-Verification.git
cd Academic-Transcript-Verification/
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt-get install tesseract-ocr
python app.py
```


