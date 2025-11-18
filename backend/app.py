from flask import Flask, render_template, request, redirect, url_for, session, make_response
import random
import mysql.connector
from questions import questions
import os
# FIX 1: Import Path for correct template folder discovery
from pathlib import Path 
from io import BytesIO
from datetime import datetime
from xhtml2pdf import pisa
from flask import render_template_string

# --- Configuration ---
# NOTE: The FLASK_SECRET_KEY fallback is fine for development but should be a true secret in production.
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'devops-exam-secret-key')

# --- Helper Functions ---

def get_db_connection():
    # Database connection details are correctly pulled from environment variables
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'rootpass'),
        database=os.getenv('MYSQL_DATABASE', 'devops_exam')
    )

def read_certificate_template():
    # Looks for 'certificate.html' in the same directory as this file
    with open(os.path.join(os.path.dirname(__file__), 'certificate.html'), 'r') as file:
        return file.read()

# --- Template Configuration (Fixing TemplateNotFound Error) ---

# 1. Define the root directory of your project (one level up from 'backend')
PROJECT_ROOT = Path(__file__).parent.parent 

# 2. Construct the absolute path to your 'frontend' folder
# This should resolve to: your-flask-app/frontend
TEMPLATE_DIR = str(PROJECT_ROOT / 'frontend')

# 3. Initialize Flask, telling it to use the 'frontend' directory for templates
# This ensures templates like 'index.html' are found in 'frontend/'
app = Flask(__name__, template_folder=TEMPLATE_DIR)

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_exam():
    # ... logic for storing user data and selecting questions (remains unchanged)
    session['name'] = request.form['name']
    session['gender'] = request.form['gender']
    session['email'] = request.form['email']
    
    # Select 15 random questions and store in session
    selected_questions = random.sample(questions, 15)
    for i, q in enumerate(selected_questions):
        q['index'] = i 
    session['questions'] = selected_questions
    
    return render_template('exam.html', 
                          name=session['name'],
                          gender=session['gender'],
                          email=session['email'],
                          questions=selected_questions)

@app.route('/submit', methods=['POST'])
def submit_exam():
    # ... Score calculation and database insertion (remains unchanged)
    try:
        # Verify all questions were answered
        questions_in_session = session.get('questions', [])
        for i in range(len(questions_in_session)):
            if f'question_{i}' not in request.form:
                return "Please answer all questions", 400
        
        db = get_db_connection()
        cursor = db.cursor()
        
        # Calculate score
        score = 0
        for i, q in enumerate(session['questions']):
            user_answer = request.form.get(f'question_{i}')
            if user_answer == q['answer']:
                score += 1

        cursor.execute(
            "INSERT INTO results (username, gender, email, score) VALUES (%s, %s, %s, %s)",
            (session['name'], session['gender'], session['email'], score)
        )
        db.commit()
        
        # Store score in session for certificate generation
        session['exam_score'] = score
        
        return render_template('result.html', 
                              name=session.get('name'),
                              score=score,
                              total=len(questions_in_session))
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        return "An error occurred while processing your exam", 500
    finally:
        # Ensure database connection is closed
        if 'db' in locals() and db.is_connected():
            db.close()

@app.route('/download_certificate')
def download_certificate():
    # ... Certificate generation logic (remains unchanged)
    try:
        # Get user details from session
        name = session.get('name', 'Exam Participant')
        score = session.get('exam_score', 0)
        
        # Read certificate template
        template = read_certificate_template()
        
        # Render template with user data
        rendered = render_template_string(template,
                                         name=name,
                                         score=score,
                                         date=datetime.now().strftime("%B %d, %Y"))
        
        # Create PDF
        pdf = BytesIO()
        pisa.CreatePDF(rendered, dest=pdf)
        pdf.seek(0)
        
        # Create response
        response = make_response(pdf.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=devops_certificate_{name.replace(" ", "_")}.pdf'
        
        return response
    except Exception as e:
        app.logger.error(f"Certificate generation error: {str(e)}")
        return "An error occurred while generating your certificate", 500

@app.route('/admin')
def admin_view():
    # ... Admin view logic (remains unchanged)
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT username, gender, email, score FROM results")
        records = cursor.fetchall()
        return render_template('admin.html', records=records)
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        return "Database error occurred", 500
    finally:
        # Ensure database connection is closed
        if 'db' in locals() and db.is_connected():
            db.close()

if __name__ == '__main__':
    # Running on 0.0.0.0 is necessary for containerization
    app.run(host='0.0.0.0', port=5000)