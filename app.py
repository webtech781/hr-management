from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from database import init_app, get_db
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import sqlite3
from datetime import datetime, timedelta
from jinja2 import Undefined
import csv
from io import StringIO
from werkzeug.wrappers import Response
import os
import hashlib  # Add this at the top
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['DATABASE'] = 'hr_system.db'

# Add these configurations
UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db():
    """Connect to the database."""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db

def init_db():
    """Initialize the database."""
    try:
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.teardown_appcontext
def close_db(error):
    """Close the database at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Login decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            flash('Admin access required')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if session.get('user_id'):
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('employee_dashboard'))
    return render_template('index.html')

def hash_password(password):
    """Create MD5 hash of the password"""
    return hashlib.md5(password.encode()).hexdigest()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password', 'error')
            return render_template('admin_login.html')
        
        # Hash the password
        password_hash = hash_password(password)
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get admin user with hashed password
            cursor.execute('''
                SELECT id, username, first_name, last_name 
                FROM users 
                WHERE username = ? 
                AND password_hash = ? 
                AND role = 'admin'
            ''', (username, password_hash))
            
            admin = cursor.fetchone()
            
            if admin:
                record_login_attempt(admin['id'], 'success')
                session.clear()
                session['user_id'] = admin['id']
                session['is_admin'] = True
                session['username'] = f"{admin['first_name']} {admin['last_name']}"
                flash(f"Welcome {admin['first_name']}!", 'success')
                return redirect(url_for('admin_dashboard'))
            
            record_login_attempt(0, 'failed')
            flash('Invalid username or password', 'error')
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            record_login_attempt(0, 'failed')
            flash('An error occurred during login', 'error')
        
    return render_template('admin_login.html')

@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('employee_login.html')
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get employee
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = ? AND role = 'employee'
            ''', (email,))
            
            employee = cursor.fetchone()
            
            if employee:
                # Generate hash the same way for comparison
                password_hash = hashlib.md5(password.encode()).hexdigest()
                
                # Debug prints
                print(f"Input password: {password}")
                print(f"Generated hash: {password_hash}")
                print(f"Stored hash: {employee['password_hash']}")
                
                if password_hash == employee['password_hash']:
                    record_login_attempt(employee['id'], 'success')
                    session.clear()
                    session['user_id'] = employee['id']
                    session['is_admin'] = False
                    session['username'] = f"{employee['first_name']} {employee['last_name']}"
                    flash(f"Welcome {employee['first_name']}!", 'success')
                    return redirect(url_for('employee_dashboard'))
            
            record_login_attempt(employee['id'] if employee else 0, 'failed')
            flash('Invalid email or password', 'error')
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            record_login_attempt(employee['id'] if employee else 0, 'failed')
            flash('An error occurred during login', 'error')
        
    return render_template('employee_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.route('/employees')
@admin_required
def view_employees():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM users 
        WHERE role = 'employee'
        ORDER BY department, first_name
    ''')
    employees = cursor.fetchall()
    return render_template('view_employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        duration = request.form['duration']
        salary = request.form['salary']
        position = request.form['position']
        department = request.form['department'] or None
        password = request.form['password']
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('add_employee'))
        
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (
                    first_name, last_name, email, phone, duration, salary,
                    position, department, password_hash, role, join_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                first_name, last_name, email, phone, duration, salary,
                position, department, generate_password_hash(password),
                'employee', datetime.now().strftime('%Y-%m-%d')
            ))
            db.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('view_employees'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
    
    return render_template('add_employee.html')

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    if session.get('is_admin'):
        return redirect(url_for('view_employees'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT id, first_name, last_name, email, position, department, duration, salary 
        FROM users WHERE id = ?
    ''', (session['user_id'],))
    employee = cursor.fetchone()
    return render_template('employee_dashboard.html', employee=employee)

@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_employee(id):
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        department = request.form['department'] or None
        
        try:
            cursor.execute('''
                UPDATE users 
                SET first_name=?, last_name=?, email=?, phone=?, 
                    position=?, department=? 
                WHERE id=? AND role='employee'
            ''', (first_name, last_name, email, phone, position, department, id))
            db.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('view_employees'))
        except sqlite3.Error as e:
            flash(f'Error updating employee: {str(e)}', 'error')
    
    cursor.execute('SELECT * FROM users WHERE id=? AND role=?', (id, 'employee'))
    employee = cursor.fetchone()
    
    if not employee:
        flash('Employee not found', 'error')
        return redirect(url_for('view_employees'))
        
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:id>')
@admin_required
def delete_employee(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM employees WHERE id=?', (id,))
    db.commit()
    flash('Employee deleted successfully!')
    return redirect(url_for('view_employees'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    cursor = db.cursor()
    
    # Get statistics with error handling
    stats = {
        'total_employees': 0,
        'pending_leaves': 0,
        'pending_tours': 0,
        'pending_tasks': 0
    }
    
    try:
        cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = ?', ('employee',))
        stats['total_employees'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM leave_requests WHERE status = ?', ('pending',))
        stats['pending_leaves'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = ?', ('pending',))
        stats['pending_tasks'] = cursor.fetchone()['count']
        
        # Only query tour_requests if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tour_requests'")
        if cursor.fetchone():
            cursor.execute('SELECT COUNT(*) as count FROM tour_requests WHERE status = ?', ('pending',))
            stats['pending_tours'] = cursor.fetchone()['count']
    except sqlite3.Error as e:
        flash(f'Error fetching statistics: {str(e)}', 'error')
    
    # Get recent leave requests
    cursor.execute('''
        SELECT lr.*, u.first_name, u.last_name 
        FROM leave_requests lr 
        JOIN users u ON lr.user_id = u.id 
        ORDER BY lr.created_at DESC LIMIT 5
    ''')
    recent_leaves = cursor.fetchall()
    
    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT a.*, u.first_name, u.last_name 
        FROM attendance a 
        JOIN users u ON a.user_id = u.id 
        WHERE date = ? 
        ORDER BY check_in DESC
    ''', (today,))
    todays_attendance = cursor.fetchall()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_leaves=recent_leaves,
                         todays_attendance=todays_attendance)

@app.route('/admin/shifts')
@admin_required
def manage_shifts():
    db = get_db()
    cursor = db.cursor()
    
    # Get all shifts for the current month
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT s.*, u.first_name, u.last_name, u.duration 
        FROM shifts s 
        JOIN users u ON s.user_id = u.id 
        WHERE strftime('%Y-%m', s.date) = ?
        ORDER BY s.date, s.shift_type
    ''', (current_month,))
    
    # Convert Row objects to dictionaries
    shifts = [dict(row) for row in cursor.fetchall()]
    
    # Get all employees and convert to dictionaries
    cursor.execute('''
        SELECT id, first_name, last_name, duration 
        FROM users 
        WHERE role = 'employee'
        ORDER BY first_name
    ''')
    employees = [dict(row) for row in cursor.fetchall()]
    
    return render_template('admin/shifts.html', 
                         shifts=shifts, 
                         employees=employees,
                         current_month=current_month)

@app.route('/admin/shifts/add', methods=['POST'])
@admin_required
def add_shift():
    if request.method == 'POST':
        user_id = request.form['employee_id']
        date = request.form['date']
        shift_type = request.form['shift_type']
        location = request.form['location']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Check if shift already exists
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM shifts 
                WHERE user_id = ? AND date = ?
            ''', (user_id, date))
            
            if cursor.fetchone()['count'] > 0:
                flash('Shift already exists for this employee on this date!', 'error')
                return redirect(url_for('manage_shifts'))
            
            # Add the new shift
            cursor.execute('''
                INSERT INTO shifts (user_id, date, shift_type, location)
                VALUES (?, ?, ?, ?)
            ''', (user_id, date, shift_type, location))
            
            db.commit()
            flash('Shift added successfully!', 'success')
            
        except sqlite3.Error as e:
            db.rollback()
            flash(f'Error adding shift: {str(e)}', 'error')
        
    return redirect(url_for('manage_shifts'))

@app.route('/admin/overtime')
@admin_required
def manage_overtime():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT o.*, u.first_name, u.last_name 
        FROM overtime o 
        JOIN users u ON o.user_id = u.id 
        ORDER BY o.date DESC
    ''')
    overtime_records = cursor.fetchall()
    
    cursor.execute('''
        SELECT id, first_name, last_name 
        FROM users 
        WHERE role = 'employee'
        ORDER BY first_name
    ''')
    employees = cursor.fetchall()
    
    return render_template('admin/overtime.html', 
                         overtime_records=overtime_records,
                         employees=employees)

@app.route('/admin/overtime/add', methods=['POST'])
@admin_required
def add_overtime():
    if request.method == 'POST':
        user_id = request.form['employee_id']
        date = request.form['date']
        hours = request.form['hours']
        reason = request.form['reason']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO overtime (user_id, date, hours, reason)
                VALUES (?, ?, ?, ?)
            ''', (user_id, date, hours, reason))
            db.commit()
            flash('Overtime record added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Error adding overtime record!', 'error')
        
    return redirect(url_for('manage_overtime'))

@app.route('/employee/leave')
@login_required
def apply_leave():
    db = get_db()
    cursor = db.cursor()
    
    # Get leave history for current user
    cursor.execute('''
        SELECT * FROM leave_requests 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    
    leave_history = cursor.fetchall()
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('employee/leave.html',
                         leave_history=leave_history,
                         today=today)

@app.route('/employee/leave/submit', methods=['POST'])
@login_required
def submit_leave():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    reason = request.form.get('reason')
    
    if not all([start_date, end_date, reason]):
        flash('Please fill all required fields', 'error')
        return redirect(url_for('apply_leave'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO leave_requests (user_id, start_date, end_date, reason, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (session['user_id'], start_date, end_date, reason))
        
        db.commit()
        flash('Leave request submitted successfully!', 'success')
        
    except Exception as e:
        print(f"Error submitting leave: {str(e)}")
        flash('Error submitting leave request', 'error')
    
    return redirect(url_for('apply_leave'))

@app.route('/employee/tasks')
@login_required
def view_tasks():
    db = get_db()
    cursor = db.cursor()
    
    # Get current and upcoming duties
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE user_id = ? 
        AND start_time >= date('now', '-1 day')  -- Show duties from yesterday onwards
        ORDER BY start_time ASC
    ''', (session['user_id'],))
    tasks = cursor.fetchall()
    
    return render_template('employee/tasks.html', tasks=tasks)

@app.route('/employee/shifts')
@login_required
def view_shifts():
    db = get_db()
    cursor = db.cursor()
    
    # Get current month's shifts
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT * FROM shifts 
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        ORDER BY date
    ''', (session['user_id'], current_month))
    shifts = cursor.fetchall()
    
    return render_template('employee/shifts.html', shifts=shifts)

@app.route('/employee/attendance')
@login_required
def attendance_history():
    db = get_db()
    cursor = db.cursor()
    
    # Get current month's attendance
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT * FROM attendance 
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        ORDER BY date DESC
    ''', (session['user_id'], current_month))
    
    attendance_records = []
    records = cursor.fetchall()
    
    for record in records:
        # Convert string timestamps to datetime objects, handling microseconds
        check_in_time = None
        check_out_time = None
        
        if record['check_in']:
            try:
                # Split on period to remove microseconds
                check_in_str = record['check_in'].split('.')[0]
                check_in_dt = datetime.strptime(check_in_str, '%Y-%m-%d %H:%M:%S')
                check_in_time = check_in_dt.strftime('%I:%M %p')
            except Exception as e:
                print(f"Error parsing check_in time: {e}")
        
        if record['check_out']:
            try:
                # Split on period to remove microseconds
                check_out_str = record['check_out'].split('.')[0]
                check_out_dt = datetime.strptime(check_out_str, '%Y-%m-%d %H:%M:%S')
                check_out_time = check_out_dt.strftime('%I:%M %p')
            except Exception as e:
                print(f"Error parsing check_out time: {e}")
        
        try:
            date_str = datetime.strptime(record['date'], '%Y-%m-%d').strftime('%B %d, %Y')
        except Exception as e:
            print(f"Error parsing date: {e}")
            date_str = record['date']
            
        attendance_records.append({
            'date': date_str,
            'check_in': check_in_time,
            'check_out': check_out_time,
            'status': record['status']
        })
    
    # Calculate statistics
    total_records = len(attendance_records)
    on_time = 0
    late = 0
    absent = 0
    
    for record in records:
        if record['status'] == 'absent':
            absent += 1
        elif record['check_in']:
            try:
                check_in_str = record['check_in'].split('.')[0]
                check_in_time = datetime.strptime(check_in_str, '%Y-%m-%d %H:%M:%S')
                if check_in_time.strftime('%H:%M:%S') <= '09:00:00':
                    on_time += 1
                else:
                    late += 1
            except Exception as e:
                print(f"Error calculating statistics: {e}")
    
    return render_template('employee/attendance.html',
                         attendance=attendance_records,
                         stats={
                             'total': total_records,
                             'on_time': on_time,
                             'late': late,
                             'absent': absent
                         })

@app.route('/employee/payroll')
@login_required
def view_payroll():
    db = get_db()
    cursor = db.cursor()
    
    # Get employee details
    cursor.execute('''
        SELECT salary, join_date FROM users WHERE id = ?
    ''', (session['user_id'],))
    employee = cursor.fetchone()
    
    # Handle case where employee record is not found
    if not employee:
        flash('Employee record not found', 'error')
        return redirect(url_for('employee_dashboard'))
    
    # Get overtime records for current month
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT * FROM overtime 
        WHERE user_id = ? 
        AND strftime('%Y-%m', date) = ?
        AND status = 'approved'
        ORDER BY date DESC
    ''', (session['user_id'], current_month))
    overtime = cursor.fetchall()
    
    # Convert employee data to dict for easier template access
    employee_data = {
        'salary': float(employee['salary'] or 0),  # Handle NULL salary
        'join_date': employee['join_date']  # Will be formatted by template filter
    }
    
    # Format today's date as string for template
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('employee/payroll.html',
                         employee=employee_data,
                         overtime=overtime,
                         today=today)

@app.route('/employee/attendance/mark', methods=['POST'])
@login_required
def mark_attendance():
    action = request.form.get('action')
    if not action or action not in ['check_in', 'check_out']:
        flash('Invalid action', 'error')
        return redirect(url_for('attendance_history'))
    
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%Y-%m-%d %H:%M:%S')  # Store without microseconds
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        if action == 'check_in':
            # Check if already checked in today
            cursor.execute('''
                SELECT * FROM attendance 
                WHERE user_id = ? AND date = ?
            ''', (session['user_id'], today))
            
            existing = cursor.fetchone()
            if existing:
                if existing['check_in']:
                    flash('Already checked in today', 'warning')
                    return redirect(url_for('attendance_history'))
                
                # Update existing record
                cursor.execute('''
                    UPDATE attendance 
                    SET check_in = ?, 
                        status = ? 
                    WHERE id = ?
                ''', (
                    current_time,
                    'late' if now.strftime('%H:%M:%S') > '09:00:00' else 'present',
                    existing['id']
                ))
            else:
                # Create new attendance record
                cursor.execute('''
                    INSERT INTO attendance (user_id, date, check_in, status)
                    VALUES (?, ?, ?, ?)
                ''', (
                    session['user_id'],
                    today,
                    current_time,
                    'late' if now.strftime('%H:%M:%S') > '09:00:00' else 'present'
                ))
            
            flash('Check-in recorded successfully', 'success')
            
        else:  # check_out
            cursor.execute('''
                SELECT * FROM attendance 
                WHERE user_id = ? AND date = ?
            ''', (session['user_id'], today))
            
            record = cursor.fetchone()
            if not record:
                flash('No check-in record found for today', 'error')
                return redirect(url_for('attendance_history'))
            
            if record['check_out']:
                flash('Already checked out today', 'warning')
                return redirect(url_for('attendance_history'))
            
            cursor.execute('''
                UPDATE attendance 
                SET check_out = ? 
                WHERE id = ?
            ''', (current_time, record['id']))
            
            flash('Check-out recorded successfully', 'success')
        
        db.commit()
        
    except Exception as e:
        print(f"Error marking attendance: {str(e)}")
        flash('Error recording attendance', 'error')
    
    return redirect(url_for('attendance_history'))

@app.route('/employee/task/update-status', methods=['POST'])
@login_required
def update_task_status():
    if request.method == 'POST':
        task_id = request.form['task_id']
        status = request.form['status']
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Verify task belongs to user
            cursor.execute('''
                SELECT user_id FROM tasks 
                WHERE id = ?
            ''', (task_id,))
            task = cursor.fetchone()
            
            if task and task['user_id'] == session['user_id']:
                cursor.execute('''
                    UPDATE tasks 
                    SET status = ? 
                    WHERE id = ?
                ''', (status, task_id))
                db.commit()
                flash('Task status updated successfully!', 'success')
            else:
                flash('Invalid task!', 'error')
                
        except sqlite3.Error as e:
            flash(f'Error updating task status: {str(e)}', 'error')
            
    return redirect(url_for('view_tasks'))

@app.route('/admin/export/<table_name>')
@admin_required
def export_data(table_name):
    """Export table data to CSV"""
    allowed_tables = {
        'employees': 'SELECT * FROM users WHERE role = "employee"',
        'attendance': 'SELECT * FROM attendance',
        'leaves': 'SELECT * FROM leave_requests',
        'tasks': 'SELECT * FROM tasks',
        'overtime': 'SELECT * FROM overtime',
        'shifts': 'SELECT * FROM shifts'
    }
    
    if table_name not in allowed_tables:
        flash('Invalid table name', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(allowed_tables[table_name])
    rows = cursor.fetchall()
    
    if not rows:
        flash('No data to export', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    # Create CSV string
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(rows[0].keys())  # Write headers
    writer.writerows([dict(row).values() for row in rows])  # Write data
    
    output = si.getvalue()
    si.close()
    
    # Create the response
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return Response(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={table_name}_{timestamp}.csv'
        }
    )

@app.route('/admin/import/<table_name>', methods=['POST'])
@admin_required
def import_data(table_name):
    """Import data from CSV file"""
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('admin_dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('admin_dashboard'))
    
    if not file.filename.endswith('.csv'):
        flash('Only CSV files are allowed', 'error')
        return redirect(url_for('admin_dashboard'))
    
    allowed_tables = {
        'employees': 'users',
        'attendance': 'attendance',
        'leaves': 'leave_requests',
        'tasks': 'tasks',
        'overtime': 'overtime',
        'shifts': 'shifts'
    }
    
    if table_name not in allowed_tables:
        flash('Invalid table name', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        # Read CSV file
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_data = csv.DictReader(stream)
        
        db = get_db()
        cursor = db.cursor()
        
        # Get column names for the table
        cursor.execute(f'PRAGMA table_info({allowed_tables[table_name]})')
        columns = [row['name'] for row in cursor.fetchall()]
        
        # Import data
        for row in csv_data:
            # Filter out invalid columns
            valid_data = {k: v for k, v in row.items() if k in columns}
            
            # Build the INSERT query
            placeholders = ','.join(['?' for _ in valid_data])
            cols = ','.join(valid_data.keys())
            query = f'INSERT INTO {allowed_tables[table_name]} ({cols}) VALUES ({placeholders})'
            
            cursor.execute(query, list(valid_data.values()))
        
        db.commit()
        flash('Data imported successfully!', 'success')
        
    except Exception as e:
        flash(f'Error importing data: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

def generate_password_hash(password):
    """Generate a consistent MD5 hash for a password"""
    return hashlib.md5(password.encode()).hexdigest()

# Test the hash generation
test_password = 'emp123'
test_hash = generate_password_hash(test_password)
print(f"Test password '{test_password}' hash: {test_hash}")

def initialize_database():
    """Initialize database on startup."""
    with app.app_context():
        if not os.path.exists(app.config['DATABASE']):
            init_db()

initialize_database()

@app.template_filter('format_date')
def format_date(date_str):
    """Convert date string to formatted date"""
    if not date_str:
        return ''
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')  # Example: January 08, 2025
    except:
        return date_str

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if not date:
        return ''
    if fmt:
        return date.strftime(fmt)
    return date.strftime('%B %d, %Y')  # Default format

@app.route('/admin/leaves')
@admin_required
def manage_leaves():
    db = get_db()
    cursor = db.cursor()
    
    # Get all leave requests with employee details
    cursor.execute('''
        SELECT lr.*, 
               u.first_name, 
               u.last_name, 
               u.department,
               u.position
        FROM leave_requests lr
        JOIN users u ON lr.user_id = u.id
        ORDER BY lr.created_at DESC
    ''')
    
    leave_requests = cursor.fetchall()
    
    # Calculate leave statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
        FROM leave_requests
    ''')
    
    stats = cursor.fetchone()
    
    return render_template('admin/leaves.html', 
                         leave_requests=leave_requests,
                         stats=stats)

@app.route('/admin/leave/update-status', methods=['POST'])
@admin_required
def update_leave_status():
    leave_id = request.form.get('leave_id')
    status = request.form.get('status')
    
    if not all([leave_id, status]) or status not in ['approved', 'rejected']:
        flash('Invalid request', 'error')
        return redirect(url_for('manage_leaves'))
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Update leave request status
        cursor.execute('''
            UPDATE leave_requests 
            SET status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, leave_id))
        
        # Get employee details for notification
        cursor.execute('''
            SELECT u.first_name, lr.start_date, lr.end_date
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            WHERE lr.id = ?
        ''', (leave_id,))
        
        leave_info = cursor.fetchone()
        
        db.commit()
        
        if leave_info:
            flash(f"Leave request for {leave_info['first_name']} ({leave_info['start_date']} to {leave_info['end_date']}) has been {status}!", 'success')
        else:
            flash(f'Leave request has been {status}!', 'success')
            
    except Exception as e:
        print(f"Error updating leave status: {str(e)}")
        flash('Error updating leave request', 'error')
        
    return redirect(url_for('manage_leaves'))

@app.route('/profile/upload-photo', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'photo' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('view_profile'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('view_profile'))
    
    if file and allowed_file(file.filename):
        # Create a unique filename
        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Delete old profile pic if exists
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('SELECT profile_pic FROM users WHERE id = ?', (session['user_id'],))
            old_pic = cursor.fetchone()['profile_pic']
            if old_pic:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], old_pic)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
        except Exception as e:
            print(f"Error removing old profile pic: {e}")
        
        # Save new file and update database
        try:
            file.save(filepath)
            cursor.execute('''
                UPDATE users 
                SET profile_pic = ?
                WHERE id = ?
            ''', (filename, session['user_id']))
            db.commit()
            flash('Profile photo updated successfully!', 'success')
        except Exception as e:
            print(f"Error saving profile pic: {e}")
            flash('Error updating profile photo', 'error')
    else:
        flash('Invalid file type. Please use PNG, JPG, JPEG, or GIF', 'error')
    
    return redirect(url_for('view_profile'))

@app.route('/profile')
@login_required
def view_profile():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM users WHERE id = ?
    ''', (session['user_id'],))
    user = cursor.fetchone()
    
    return render_template('profile.html', user=user)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/credentials')
@admin_required
def view_credentials():
    db = get_db()
    cursor = db.cursor()
    
    # Get all users with their credentials
    cursor.execute('''
        SELECT id, first_name, last_name, email, username, 
               role, department, position, created_at
        FROM users
        ORDER BY role DESC, department, first_name
    ''')
    
    users = cursor.fetchall()
    return render_template('admin/credentials.html', users=users)

@app.route('/admin/login-history')
@admin_required
def view_login_history():
    db = get_db()
    cursor = db.cursor()
    
    # Get login history with user details
    cursor.execute('''
        SELECT 
            lh.*,
            u.first_name,
            u.last_name,
            u.email,
            u.role,
            u.department
        FROM login_history lh
        JOIN users u ON lh.user_id = u.id
        ORDER BY lh.login_time DESC
        LIMIT 1000
    ''')
    
    history = cursor.fetchall()
    return render_template('admin/login_history.html', history=history)

# Modify the login functions to record login attempts
def record_login_attempt(user_id, status):
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO login_history (
                user_id, ip_address, user_agent, status
            ) VALUES (?, ?, ?, ?)
        ''', (
            user_id,
            request.remote_addr,
            request.user_agent.string,
            status
        ))
        
        db.commit()
    except Exception as e:
        print(f"Error recording login attempt: {e}")

if __name__ == '__main__':
    app.run(debug=True) 