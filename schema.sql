-- Drop existing tables if they exist
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS leave_requests;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS overtime;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS tour_requests;
DROP TABLE IF EXISTS login_history;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    username TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    position TEXT,
    department TEXT,
    salary REAL,
    duration INTEGER,
    join_date TEXT,
    profile_pic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create attendance table
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    check_in TIMESTAMP,
    check_out TIMESTAMP,
    status TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create leave_requests table if not exists
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create tour_requests table
CREATE TABLE tour_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    location TEXT NOT NULL,
    purpose TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create overtime table
CREATE TABLE overtime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    hours REAL NOT NULL,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create shifts table
CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    shift_type TEXT NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create login_history table
CREATE TABLE login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    status TEXT NOT NULL, -- 'success' or 'failed'
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert admin users with MD5 hashed passwords
INSERT INTO users (
    first_name, last_name, email, username, password_hash, role, position
) VALUES 
    -- Main Admin (password: admin123)
    ('John', 'Admin', 'admin@example.com', 'admin',
    '0192023a7bbd73250516f069df18b500', -- MD5 hash of 'admin123'
    'admin', 'System Administrator'),
    
    -- HR Admin (password: hradmin456)
    ('Sarah', 'Manager', 'hr.admin@example.com', 'hradmin',
    '9b3c20b2685b76c64c5ea476d572d17b', -- MD5 hash of 'hradmin456'
    'admin', 'HR Administrator'),
    
    -- Finance Admin (password: finadmin789)
    ('Michael', 'Director', 'finance.admin@example.com', 'finadmin',
    '45d1e4a76dc5d868d0f7c9943022c77f', -- MD5 hash of 'finadmin789'
    'admin', 'Finance Administrator');

-- Insert multiple employees with their data (with MD5 hashed passwords)
INSERT INTO users (
    first_name, last_name, email, phone, password_hash, role, position, department, salary, duration
) VALUES
    -- IT Department
    ('Alex', 'Smith', 'alex.smith@example.com', 
    '+1 (555) 101-1001',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Senior Developer', 'IT', 85000, 8),
    ('Emma', 'Johnson', 'emma.j@example.com', 
    '+1 (555) 101-1002',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Full Stack Developer', 'IT', 75000, 5),
    ('Michael', 'Brown', 'michael.b@example.com', 
    '+1 (555) 101-1003',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'DevOps Engineer', 'IT', 90000, 6),
    ('Sarah', 'Davis', 'sarah.d@example.com', 
    '+1 (555) 101-1004',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'UI/UX Designer', 'IT', 70000, 4),
    ('James', 'Wilson', 'james.w@example.com', 
    '+1 (555) 101-1005',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'System Administrator', 'IT', 80000, 7),

    -- HR Department
    ('Lisa', 'Anderson', 'lisa.a@example.com', 
    '+1 (555) 101-1006',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'HR Manager', 'HR', 75000, 6),
    ('David', 'Taylor', 'david.t@example.com', 
    '+1 (555) 101-1007',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Recruiter', 'HR', 65000, 4),
    ('Emily', 'Thomas', 'emily.t@example.com', 
    '+1 (555) 101-1008',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'HR Specialist', 'HR', 60000, 3),
    ('Daniel', 'Moore', 'daniel.m@example.com', 
    '+1 (555) 101-1009',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Training Coordinator', 'HR', 62000, 4),
    ('Sophie', 'Clark', 'sophie.c@example.com', 
    '+1 (555) 101-1010',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'HR Assistant', 'HR', 55000, 2),

    -- Finance Department
    ('William', 'White', 'william.w@example.com', 
    '+1 (555) 101-1011',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Finance Manager', 'Finance', 95000, 8),
    ('Oliver', 'Hall', 'oliver.h@example.com', 
    '+1 (555) 101-1012',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Senior Accountant', 'Finance', 80000, 6),
    ('Isabella', 'Lee', 'isabella.l@example.com', 
    '+1 (555) 101-1013',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Financial Analyst', 'Finance', 75000, 5),
    ('Ethan', 'Baker', 'ethan.b@example.com', 
    '+1 (555) 101-1014',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Accountant', 'Finance', 65000, 4),
    ('Ava', 'Carter', 'ava.c@example.com', 
    '+1 (555) 101-1015',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Payroll Specialist', 'Finance', 62000, 3),

    -- Marketing Department
    ('Noah', 'King', 'noah.k@example.com', 
    '+1 (555) 101-1016',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Marketing Director', 'Marketing', 92000, 7),
    ('Mia', 'Wright', 'mia.w@example.com', 
    '+1 (555) 101-1017',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Marketing Manager', 'Marketing', 82000, 6),
    ('Lucas', 'Lopez', 'lucas.l@example.com', 
    '+1 (555) 101-1018',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Digital Marketing Specialist', 'Marketing', 68000, 4),
    ('Sophia', 'Hill', 'sophia.h@example.com', 
    '+1 (555) 101-1019',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Content Creator', 'Marketing', 65000, 3),
    ('Jack', 'Scott', 'jack.s@example.com', 
    '+1 (555) 101-1020',
    '0314ee502c6f4e284128ad14e84e37d5',
    'employee', 'Social Media Manager', 'Marketing', 60000, 3);

-- Insert sample tasks for employees
INSERT INTO tasks (user_id, title, location, start_time, end_time, description, status)
VALUES 
    -- IT Department Tasks
    (2, 'System Update', 'Server Room', '09:00', '17:00', 'Perform system updates and maintenance', 'pending'),
    (2, 'Code Review', 'Office', '14:00', '16:00', 'Review sprint code', 'in_progress'),
    (3, 'Database Optimization', 'Server Room', '10:00', '15:00', 'Optimize database performance', 'pending'),
    (4, 'UI Design Review', 'Meeting Room 2', '13:00', '15:00', 'Review new UI designs', 'completed'),
    (5, 'Network Maintenance', 'IT Lab', '09:00', '18:00', 'Quarterly network maintenance', 'pending'),

    -- HR Department Tasks
    (6, 'Interview Candidates', 'Meeting Room 1', '10:00', '16:00', 'Interview software developers', 'in_progress'),
    (7, 'Training Session', 'Training Room', '09:00', '12:00', 'New employee orientation', 'pending'),
    (8, 'Benefits Review', 'HR Office', '14:00', '17:00', 'Annual benefits review meeting', 'pending'),
    (9, 'Employee Workshop', 'Conference Room', '13:00', '15:00', 'Team building workshop', 'scheduled'),
    (10, 'Document Processing', 'HR Office', '09:00', '17:00', 'Process employee documents', 'in_progress'),

    -- Finance Department Tasks
    (11, 'Budget Review', 'Finance Office', '09:00', '11:00', 'Q2 budget review meeting', 'scheduled'),
    (12, 'Audit Preparation', 'Finance Office', '10:00', '18:00', 'Prepare for annual audit', 'pending'),
    (13, 'Financial Report', 'Meeting Room 3', '14:00', '16:00', 'Monthly financial report preparation', 'in_progress'),
    (14, 'Expense Processing', 'Finance Office', '09:00', '17:00', 'Process employee expenses', 'pending'),
    (15, 'Payroll Processing', 'Finance Office', '09:00', '15:00', 'Monthly payroll processing', 'scheduled');

-- Insert shifts for employees
INSERT INTO shifts (user_id, date, shift_type, location)
VALUES 
    -- IT Department Shifts
    (2, date('now'), 'Morning', 'Main Office'),
    (3, date('now'), 'Evening', 'Main Office'),
    (4, date('now'), 'Morning', 'Design Studio'),
    (5, date('now'), 'Night', 'Server Room'),

    -- HR Department Shifts
    (6, date('now'), 'Morning', 'HR Office'),
    (7, date('now'), 'Morning', 'Recruitment Center'),
    (8, date('now'), 'Evening', 'HR Office'),
    (9, date('now'), 'Morning', 'Training Center'),

    -- Finance Department Shifts
    (11, date('now'), 'Morning', 'Finance Office'),
    (12, date('now'), 'Evening', 'Finance Office'),
    (13, date('now'), 'Morning', 'Analysis Room'),
    (14, date('now'), 'Morning', 'Finance Office');

-- Insert overtime records
INSERT INTO overtime (user_id, date, hours, reason, status)
VALUES
    (2, date('now', '-1 day'), 2.5, 'Emergency system fix', 'approved'),
    (3, date('now', '-2 day'), 3.0, 'Database migration', 'approved'),
    (4, date('now', '-1 day'), 2.0, 'Project deadline', 'pending'),
    (11, date('now', '-3 day'), 2.0, 'Month-end closing', 'approved'),
    (12, date('now', '-2 day'), 3.0, 'Audit preparation', 'pending');

-- Insert attendance records
INSERT INTO attendance (user_id, date, check_in, check_out, status)
VALUES
    (2, date('now'), datetime('now', '-8 hours'), datetime('now'), 'present'),
    (3, date('now'), datetime('now', '-7 hours'), datetime('now'), 'present'),
    (4, date('now'), datetime('now', '-9 hours'), datetime('now'), 'present'),
    (6, date('now'), datetime('now', '-8 hours'), datetime('now'), 'present'),
    (11, date('now'), datetime('now', '-8 hours'), datetime('now'), 'present');

-- Insert leave requests
INSERT INTO leave_requests (user_id, start_date, end_date, reason, status)
VALUES
    (2, date('now', '+5 days'), date('now', '+7 days'), 'Family vacation', 'pending'),
    (6, date('now', '+10 days'), date('now', '+12 days'), 'Medical appointment', 'approved'),
    (11, date('now', '+15 days'), date('now', '+16 days'), 'Personal work', 'pending');

-- Create shifts for all employees for next 3 months
WITH RECURSIVE dates(date) AS (
  SELECT date('now')
  UNION ALL
  SELECT date(date, '+1 day')
  FROM dates
  WHERE date < date('now', '+3 months')
)
INSERT INTO shifts (user_id, date, shift_type, location)
SELECT 
    u.id,
    d.date,
    CASE (strftime('%w', d.date) + u.id) % 3
        WHEN 0 THEN 'Morning'   -- 9 AM to 5 PM
        WHEN 1 THEN 'Evening'   -- 4 PM to 12 AM
        WHEN 2 THEN 'Night'     -- 12 AM to 8 AM
    END as shift_type,
    CASE u.department
        WHEN 'IT' THEN CASE (strftime('%w', d.date) + u.id) % 2
            WHEN 0 THEN 'Main Office'
            WHEN 1 THEN 'Server Room'
        END
        WHEN 'HR' THEN CASE (strftime('%w', d.date) + u.id) % 2
            WHEN 0 THEN 'HR Office'
            WHEN 1 THEN 'Training Center'
        END
        WHEN 'Finance' THEN CASE (strftime('%w', d.date) + u.id) % 2
            WHEN 0 THEN 'Finance Office'
            WHEN 1 THEN 'Analysis Room'
        END
        WHEN 'Marketing' THEN CASE (strftime('%w', d.date) + u.id) % 2
            WHEN 0 THEN 'Marketing Office'
            WHEN 1 THEN 'Creative Studio'
        END
        ELSE 'Main Office'
    END as location
FROM dates d
CROSS JOIN users u
WHERE u.role = 'employee'
AND strftime('%w', d.date) NOT IN ('0', '6')  -- Exclude weekends
ORDER BY d.date, u.id;

-- Create weekly recurring tasks for employees
INSERT INTO tasks (user_id, title, location, start_time, end_time, description, status)
SELECT 
    u.id,
    CASE u.department
        WHEN 'IT' THEN 'Weekly System Maintenance'
        WHEN 'HR' THEN 'Weekly Team Meeting'
        WHEN 'Finance' THEN 'Weekly Financial Review'
        WHEN 'Marketing' THEN 'Weekly Campaign Update'
        ELSE 'Weekly Department Meeting'
    END as title,
    CASE u.department
        WHEN 'IT' THEN 'Server Room'
        WHEN 'HR' THEN 'Conference Room'
        WHEN 'Finance' THEN 'Finance Office'
        WHEN 'Marketing' THEN 'Marketing Office'
        ELSE 'Main Office'
    END as location,
    CASE (u.id % 2)
        WHEN 0 THEN '09:00'
        WHEN 1 THEN '14:00'
    END as start_time,
    CASE (u.id % 2)
        WHEN 0 THEN '10:30'
        WHEN 1 THEN '15:30'
    END as end_time,
    'Regular weekly department tasks and updates' as description,
    'scheduled' as status
FROM users u
WHERE u.role = 'employee';

-- Create monthly department meetings
INSERT INTO tasks (user_id, title, location, start_time, end_time, description, status)
SELECT 
    u.id,
    'Monthly Department Review' as title,
    CASE u.department
        WHEN 'IT' THEN 'IT Conference Room'
        WHEN 'HR' THEN 'HR Conference Room'
        WHEN 'Finance' THEN 'Finance Conference Room'
        WHEN 'Marketing' THEN 'Marketing Conference Room'
        ELSE 'Main Conference Room'
    END as location,
    '10:00' as start_time,
    '12:00' as end_time,
    'Monthly department performance review and planning' as description,
    'scheduled' as status
FROM users u
WHERE u.role = 'employee'
AND u.position LIKE '%Manager%' OR u.position LIKE '%Director%' OR u.position LIKE '%Senior%';

-- Create initial attendance records for current month
INSERT INTO attendance (user_id, date, check_in, check_out, status)
SELECT 
    u.id,
    date('now', '-' || (abs(random() % 30) + 1) || ' days') as date,
    datetime('now', '-' || (abs(random() % 30) + 1) || ' days', '+9 hours') as check_in,
    datetime('now', '-' || (abs(random() % 30) + 1) || ' days', '+17 hours') as check_out,
    CASE (abs(random() % 10))
        WHEN 0 THEN 'late'
        WHEN 9 THEN 'early_leave'
        ELSE 'present'
    END as status
FROM users u
WHERE u.role = 'employee';

-- Create overtime requests for the past month
INSERT INTO overtime (user_id, date, hours, reason, status)
SELECT 
    u.id,
    date('now', '-' || (abs(random() % 30) + 1) || ' days') as date,
    (abs(random() % 3) + 1) as hours,
    CASE u.department
        WHEN 'IT' THEN 'Emergency system maintenance'
        WHEN 'HR' THEN 'Urgent recruitment process'
        WHEN 'Finance' THEN 'Month-end closing'
        WHEN 'Marketing' THEN 'Campaign deadline'
        ELSE 'Project completion'
    END as reason,
    CASE (abs(random() % 3))
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'approved'
        ELSE 'rejected'
    END as status
FROM users u
WHERE u.role = 'employee'
AND (abs(random() % 3) = 0);  -- Only create overtime for some employees

-- Add some sample leave requests
INSERT INTO leave_requests (user_id, start_date, end_date, reason, status)
SELECT 
    u.id,
    date('now', '+' || (abs(random() % 30) + 1) || ' days') as start_date,
    date('now', '+' || (abs(random() % 30) + 2) || ' days') as end_date,
    CASE (abs(random() % 4))
        WHEN 0 THEN 'Annual Leave'
        WHEN 1 THEN 'Sick Leave'
        WHEN 2 THEN 'Personal Leave'
        ELSE 'Family Emergency'
    END as reason,
    CASE (abs(random() % 3))
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'approved'
        ELSE 'rejected'
    END as status
FROM users u
WHERE u.role = 'employee'
LIMIT 10;