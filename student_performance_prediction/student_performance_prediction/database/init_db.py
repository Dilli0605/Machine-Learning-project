"""
====================================================================
SQLite Database Initialization Script
====================================================================
Creates the required tables:
1. admin (id, username, password, created_at)
2. students (id, name, email, roll_number, department, semester, password, created_at)
3. academic_details (id, student_id, attendance, previous_marks, internal_marks, study_hours, assignment_score, absences, updated_at)
4. prediction_history (id, student_id, attendance, previous_marks, internal_marks, study_hours, assignment_score, absences, predicted_marks, expected_category, performance_level, prediction_date)
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'student_system.db')

def initialize_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Admin Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Students Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        roll_number TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. Academic Details Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS academic_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER UNIQUE NOT NULL,
        attendance REAL NOT NULL,
        previous_marks REAL NOT NULL,
        internal_marks REAL NOT NULL,
        study_hours REAL NOT NULL,
        assignment_score REAL NOT NULL,
        absences INTEGER NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    ''')

    # 4. Prediction History Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prediction_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        attendance REAL NOT NULL,
        previous_marks REAL NOT NULL,
        internal_marks REAL NOT NULL,
        study_hours REAL NOT NULL,
        assignment_score REAL NOT NULL,
        absences INTEGER NOT NULL,
        predicted_marks REAL NOT NULL,
        expected_category TEXT NOT NULL,
        performance_level TEXT NOT NULL,
        prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
    ''')

    # Seed Default Admin Account
    cursor.execute('''
    INSERT OR IGNORE INTO admin (id, username, password)
    VALUES (1, 'admin', 'admin123')
    ''')

    # Seed Sample Students if empty
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ('Aarav Sharma', 'aarav.sharma@college.edu', 'CS2026-001', 'Computer Science', 6, 'student123'),
            ('Diya Patel', 'diya.patel@college.edu', 'CS2026-002', 'Computer Science', 6, 'student123'),
            ('Rohan Verma', 'rohan.verma@college.edu', 'IT2026-003', 'Information Technology', 6, 'student123'),
            ('Sneha Iyer', 'sneha.iyer@college.edu', 'EC2026-004', 'Electronics & Comm', 6, 'student123'),
            ('Vikram Nair', 'vikram.nair@college.edu', 'CS2026-005', 'Computer Science', 6, 'student123'),
        ]
        cursor.executemany('''
        INSERT INTO students (name, email, roll_number, department, semester, password)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_students)

        # Seed sample predictions
        sample_preds = [
            (1, 92, 88, 90, 4.5, 95, 2, 89.4, 'Distinction', 'High Performer'),
            (2, 78, 72, 75, 3.0, 80, 6, 74.2, 'First Class', 'Good Potential'),
            (3, 65, 58, 60, 2.0, 65, 9, 59.8, 'Second Class', 'Average / Moderate'),
            (4, 95, 94, 95, 5.5, 98, 1, 95.8, 'Distinction', 'High Performer'),
            (5, 52, 42, 48, 1.0, 50, 14, 43.1, 'Pass Class', 'Average / Moderate'),
        ]
        cursor.executemany('''
        INSERT INTO prediction_history (
            student_id, attendance, previous_marks, internal_marks,
            study_hours, assignment_score, absences, predicted_marks,
            expected_category, performance_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_preds)

    conn.commit()
    conn.close()
    print(f" Database successfully initialized at: {DB_PATH}")

if __name__ == '__main__':
    initialize_database()
