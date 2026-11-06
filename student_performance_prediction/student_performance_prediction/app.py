"""
====================================================================
Student Performance Prediction System Using Machine Learning
Main Flask Application Entrypoint
====================================================================
This module implements the full web server for the student performance
prediction system. It manages authentication for both Students and Admins,
queries SQLite database tables, loads the trained Random Forest model using
Joblib, handles single/batch predictions, and provides RESTful endpoints.
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Initialize Flask Application
app = Flask(__name__)
app.secret_key = "student_performance_secret_key_2026_super_secure"

# Base configuration paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'student_system.db')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'student_performance_model.pkl')
METRICS_PATH = os.path.join(BASE_DIR, 'models', 'model_metrics.json')

# Helper: Connect to SQLite Database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Helper: Load Machine Learning Model
def load_ml_model():
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return None
    return None

# Classification rule based on predicted percentage
def categorize_marks(marks):
    if marks >= 85:
        return {
            'category': 'Distinction',
            'level': 'High Performer',
            'grade': 'O (Outstanding)',
            'risk': 'Low',
            'badge': 'bg-success'
        }
    elif marks >= 70:
        return {
            'category': 'First Class',
            'level': 'Good Potential',
            'grade': 'A (Very Good)',
            'risk': 'Low',
            'badge': 'bg-primary'
        }
    elif marks >= 55:
        return {
            'category': 'Second Class',
            'level': 'Average / Moderate',
            'grade': 'B (Good)',
            'risk': 'Moderate',
            'badge': 'bg-info text-dark'
        }
    elif marks >= 40:
        return {
            'category': 'Pass Class',
            'level': 'Average / Moderate',
            'grade': 'C (Pass)',
            'risk': 'High',
            'badge': 'bg-warning text-dark'
        }
    else:
        return {
            'category': 'At-Risk',
            'level': 'Critical Support Needed',
            'grade': 'F (Fail)',
            'risk': 'Severe',
            'badge': 'bg-danger'
        }

# Generate academic improvement suggestions
def generate_recommendations(attendance, prev_marks, internal, study_hours, assignment, absences):
    recs = []
    if attendance < 75:
        recs.append(f"Critical: Attendance is {attendance}%. Minimum 75% required to sit for University Examinations.")
    elif attendance < 85:
        recs.append(f"Increase attendance from {attendance}% to above 85% to gain internal moderation advantage.")

    if study_hours < 2.5:
        recs.append(f"Current self-study ({study_hours} hrs/day) is below recommended 3.5 hrs. Establish a dedicated study schedule.")
    else:
        recs.append(f"Commendable study dedication ({study_hours} hrs/day). Focus on solving previous 5 years' question papers.")

    if internal < 60:
        recs.append(f"Internal score ({internal}%) needs attention. Meet course faculty for doubt clarification.")

    if assignment < 75:
        recs.append(f"Assignment completion score ({assignment}%) is low. Timely completion directly enhances exam readiness.")

    if absences > 8:
        recs.append(f"High number of absences ({absences} days). Minimize unexcused leaves before final examinations.")

    if not recs:
        recs.append("Excellent academic indicators across all metrics. Maintain consistency to secure top university rank.")
    return recs

# -------------------------------------------------------------
# Public Routes
# -------------------------------------------------------------
@app.route('/')
def home():
    """Home landing page with project overview."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Unified login for Student and Administrator."""
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email_or_user = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()

        if user_type == 'admin':
            admin = conn.execute(
                'SELECT * FROM admin WHERE username = ? AND password = ?',
                (email_or_user, password)
            ).fetchone()
            conn.close()

            if admin:
                session['user_id'] = admin['id']
                session['username'] = admin['username']
                session['role'] = 'admin'
                flash('Admin logged in successfully.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid Admin username or password.', 'danger')

        else: # Student login
            student = conn.execute(
                'SELECT * FROM students WHERE (email = ? OR roll_number = ?) AND password = ?',
                (email_or_user, email_or_user, password)
            ).fetchone()
            conn.close()

            if student:
                session['user_id'] = student['id']
                session['student_name'] = student['name']
                session['roll_number'] = student['roll_number']
                session['role'] = 'student'
                flash(f'Welcome back, {student["name"]}!', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid student credentials. Please check your Email / Roll No and password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration route."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        roll_number = request.form.get('roll_number')
        department = request.form.get('department')
        semester = request.form.get('semester')
        password = request.form.get('password')

        if not all([name, email, roll_number, department, semester, password]):
            flash('All fields are required.', 'warning')
            return redirect(url_for('register'))

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO students (name, email, roll_number, department, semester, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, email, roll_number, department, semester, password))
            conn.commit()
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email or Roll Number is already registered.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logs out current user and clears session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# -------------------------------------------------------------
# Student Module Routes
# -------------------------------------------------------------
@app.route('/student/dashboard')
def student_dashboard():
    """Student portal dashboard with recent predictions and academic record."""
    if 'role' not in session or session['role'] != 'student':
        flash('Please login as a student to access this portal.', 'warning')
        return redirect(url_for('login'))

    student_id = session['user_id']
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    predictions = conn.execute('''
        SELECT * FROM prediction_history
        WHERE student_id = ?
        ORDER BY prediction_date DESC
    ''', (student_id,)).fetchall()
    conn.close()

    return render_template('student_dashboard.html', student=student, predictions=predictions)

@app.route('/student/predict', methods=['GET', 'POST'])
def predict():
    """Enter academic parameters and compute Machine Learning prediction."""
    if 'role' not in session or session['role'] != 'student':
        flash('Please login to run academic predictions.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            attendance = float(request.form.get('attendance', 0))
            previous_marks = float(request.form.get('previous_marks', 0))
            internal_marks = float(request.form.get('internal_marks', 0))
            study_hours = float(request.form.get('study_hours', 0))
            assignment_score = float(request.form.get('assignment_score', 0))
            absences = int(request.form.get('absences', 0))

            # Input validation
            if not (0 <= attendance <= 100 and 0 <= previous_marks <= 100 and 0 <= internal_marks <= 100):
                flash('Percentage values must be between 0 and 100.', 'danger')
                return redirect(url_for('predict'))

            # Load ML model
            model = load_ml_model()
            if model is None:
                # Fallback calculation if model file not yet trained
                pred_val = 3.5 + 0.15*attendance + 0.38*previous_marks + 0.29*internal_marks + 1.2*study_hours + 0.1*assignment_score - 0.45*absences
            else:
                features = np.array([[attendance, previous_marks, internal_marks, study_hours, assignment_score, absences]])
                pred_val = model.predict(features)[0]

            predicted_marks = max(5.0, min(100.0, round(float(pred_val), 1)))
            cat_info = categorize_marks(predicted_marks)
            recommendations = generate_recommendations(attendance, previous_marks, internal_marks, study_hours, assignment_score, absences)

            # Save prediction to SQLite database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prediction_history (
                    student_id, attendance, previous_marks, internal_marks,
                    study_hours, assignment_score, absences, predicted_marks,
                    expected_category, performance_level, prediction_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'], attendance, previous_marks, internal_marks,
                study_hours, assignment_score, absences, predicted_marks,
                cat_info['category'], cat_info['level'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            # Also update academic details table
            cursor.execute('''
                INSERT OR REPLACE INTO academic_details (
                    student_id, attendance, previous_marks, internal_marks,
                    study_hours, assignment_score, absences, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session['user_id'], attendance, previous_marks, internal_marks,
                study_hours, assignment_score, absences, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            conn.close()

            return render_template(
                'result.html',
                predicted_marks=predicted_marks,
                category=cat_info['category'],
                level=cat_info['level'],
                grade=cat_info['grade'],
                risk=cat_info['risk'],
                badge=cat_info['badge'],
                inputs={
                    'attendance': attendance,
                    'previous_marks': previous_marks,
                    'internal_marks': internal_marks,
                    'study_hours': study_hours,
                    'assignment_score': assignment_score,
                    'absences': absences
                },
                recommendations=recommendations
            )

        except Exception as e:
            flash(f'Prediction error: {str(e)}', 'danger')
            return redirect(url_for('predict'))

    return render_template('predict.html')

# -------------------------------------------------------------
# Admin Module Routes
# -------------------------------------------------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    """Administrator portal overview with statistics, charts, and counts."""
    if 'role' not in session or session['role'] != 'admin':
        flash('Admin privileges required.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_predictions = conn.execute('SELECT COUNT(*) FROM prediction_history').fetchone()[0]
    avg_score = conn.execute('SELECT AVG(predicted_marks) FROM prediction_history').fetchone()[0] or 0
    at_risk_count = conn.execute("SELECT COUNT(*) FROM prediction_history WHERE expected_category = 'At-Risk'").fetchone()[0]

    # Category breakdown for Chart.js
    categories_data = conn.execute('''
        SELECT expected_category, COUNT(*) as count
        FROM prediction_history
        GROUP BY expected_category
    ''').fetchall()

    recent_predictions = conn.execute('''
        SELECT p.*, s.name as student_name, s.roll_number, s.department
        FROM prediction_history p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.prediction_date DESC
        LIMIT 8
    ''').fetchall()

    conn.close()

    cat_labels = [row['expected_category'] for row in categories_data]
    cat_counts = [row['count'] for row in categories_data]

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_predictions=total_predictions,
        avg_score=round(avg_score, 1),
        at_risk_count=at_risk_count,
        cat_labels=cat_labels,
        cat_counts=cat_counts,
        recent_predictions=recent_predictions
    )

@app.route('/admin/students')
def admin_students():
    """View all registered students with academic performance summary."""
    if 'role' not in session or session['role'] != 'admin':
        flash('Admin access required.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    students = conn.execute('''
        SELECT s.*,
               a.attendance, a.previous_marks, a.internal_marks, a.study_hours,
               (SELECT predicted_marks FROM prediction_history WHERE student_id = s.id ORDER BY prediction_date DESC LIMIT 1) as latest_pred,
               (SELECT expected_category FROM prediction_history WHERE student_id = s.id ORDER BY prediction_date DESC LIMIT 1) as latest_cat
        FROM students s
        LEFT JOIN academic_details a ON s.id = a.student_id
        ORDER BY s.id DESC
    ''').fetchall()
    conn.close()

    return render_template('students_list.html', students=students)

@app.route('/admin/history')
def admin_history():
    """View all student prediction history records."""
    if 'role' not in session or session['role'] != 'admin':
        flash('Admin access required.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    history = conn.execute('''
        SELECT p.*, s.name as student_name, s.roll_number, s.department
        FROM prediction_history p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.prediction_date DESC
    ''').fetchall()
    conn.close()

    return render_template('history.html', history=history)

@app.route('/admin/train', methods=['GET', 'POST'])
def admin_train():
    """Facility to retrain machine learning model using CSV dataset."""
    if 'role' not in session or session['role'] != 'admin':
        flash('Admin privileges required.', 'warning')
        return redirect(url_for('login'))

    metrics = None
    if os.path.exists(METRICS_PATH):
        try:
            import json
            with open(METRICS_PATH, 'r') as f:
                metrics = json.load(f)
        except Exception:
            metrics = None

    if request.method == 'POST':
        # Check if CSV file uploaded or use default
        file = request.files.get('dataset_file')
        dataset_path = os.path.join(BASE_DIR, 'dataset', 'student_data.csv')

        if file and file.filename.endswith('.csv'):
            file.save(dataset_path)
            flash('Uploaded new CSV dataset. Retraining model...', 'info')

        try:
            # Import and execute train_model pipeline
            from train_model import train_and_save_model
            metrics = train_and_save_model(dataset_path)
            flash('Machine Learning model retrained and saved successfully!', 'success')
        except Exception as e:
            flash(f'Model training failed: {str(e)}', 'danger')

    return render_template('train.html', metrics=metrics)

# -------------------------------------------------------------
# REST API (For frontend Chart.js & dynamic fetches)
# -------------------------------------------------------------
@app.route('/api/stats')
def api_stats():
    conn = get_db_connection()
    students_count = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    preds = conn.execute('SELECT attendance, previous_marks, internal_marks, study_hours, predicted_marks FROM prediction_history').fetchall()
    conn.close()

    return jsonify({
        'total_students': students_count,
        'records': [dict(row) for row in preds]
    })

if __name__ == '__main__':
    # Ensure database tables exist
    from database.init_db import initialize_database
    initialize_database()

    print("================================================================")
    print(" Student Performance Prediction System (Flask + Scikit-Learn)")
    print(" Server running on: http://127.0.0.1:5000")
    print(" Default Admin: admin / admin123")
    print("================================================================")
    app.run(debug=True, host='0.0.0.0', port=5000)
