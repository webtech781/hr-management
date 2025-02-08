import sqlite3
from flask import g
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
import hashlib

DATABASE = 'hr_system.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def reset_db():
    """Delete the existing database file if it exists"""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

def init_db():
    """Initialize the database with all tables"""
    # First reset the database
    reset_db()
    
    db = get_db()
    cursor = db.cursor()
    
    # Create all tables
    tables = [
        # Users table
        '''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            role TEXT NOT NULL,
            position TEXT,
            department TEXT,
            duration INTEGER,
            salary INTEGER,
            join_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        
        # Attendance table
        '''CREATE TABLE attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            check_in TIMESTAMP,
            check_out TIMESTAMP,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        # Leave requests table
        '''CREATE TABLE leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        # Tour requests table
        '''CREATE TABLE tour_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination TEXT,
            start_date TEXT,
            end_date TEXT,
            purpose TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        # Tasks table
        '''CREATE TABLE tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''',
        
        # Shifts table
        '''CREATE TABLE shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            shift_type TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, date)
        ) STRICT''',
        
        # Overtime table
        '''CREATE TABLE overtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            hours INTEGER NOT NULL,
            reason TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )'''
    ]
    
    # Create each table
    for table in tables:
        cursor.execute(table)
    
    # Create default admin user
    now = datetime.now().strftime('%Y-%m-%d')
    admin_password = generate_password_hash('admin123')
    
    cursor.execute('''
        INSERT INTO users (
            username, email, password_hash, first_name, last_name,
            role, position, join_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'admin', 'admin@example.com', admin_password, 'Admin', 'User',
        'admin', 'Administrator', now
    ))
    
    db.commit()

def hash_password(password):
    """Create MD5 hash of the password"""
    return hashlib.md5(password.encode()).hexdigest()

def init_test_users():
    """Initialize test admin and employee users"""
    db = get_db()
    cursor = db.cursor()
    
    # Create test admin with hashed password
    admin_hash = hash_password('admin123')
    cursor.execute('''
        INSERT OR REPLACE INTO users (
            username, email, password_hash, first_name, last_name, role, position
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@example.com', admin_hash, 'John', 'Admin', 'admin', 'System Administrator'))
    
    # Create test employee with hashed password
    emp_hash = hash_password('emp123')
    cursor.execute('''
        INSERT OR REPLACE INTO users (
            email, password_hash, first_name, last_name, role, position, department, salary, duration
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('alex.smith@example.com', emp_hash, 'Alex', 'Smith', 'employee', 'Senior Developer', 'IT', 85000, 8))
    
    db.commit()

def init_app(app):
    """Initialize the Flask application with database functions"""
    app.teardown_appcontext(close_db)
    
    # Create tables within app context
    with app.app_context():
        if app.config.get('RESET_DB_ON_START', False):
            init_db() 