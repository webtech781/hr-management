# HR Management System

A comprehensive HR Management System built with Flask, designed to handle employee management, attendance tracking, leave management, and more.

## Features

- **User Authentication**
  - Separate login for employees and administrators
  - Secure password hashing
  - Login history tracking

- **Employee Management**
  - Employee profiles with photo upload
  - Department organization
  - Salary information
  - Contact details

- **Attendance System**
  - Check-in/Check-out functionality
  - Attendance history
  - Late arrival tracking
  - Monthly attendance reports

- **Leave Management**
  - Leave requests submission
  - Admin approval workflow
  - Leave history
  - Multiple leave types

- **Task Management**
  - Task assignment
  - Progress tracking
  - Task history

- **Shift Management**
  - Shift scheduling
  - Shift history
  - Location tracking

- **Overtime Management**
  - Overtime requests
  - Admin approval
  - Overtime calculations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Windows Installation

1. Install Python:
   ```bash
   # Download Python from https://www.python.org/downloads/
   # During installation, check "Add Python to PATH"
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/webtech781/hr-management.git
   # Or download and extract the ZIP file
   ```

3. Create a virtual environment:
   ```bash
   cd hr-management
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```bash
   flask init-db
   ```

6. Run the application:
   ```bash
   flask run
   ```

### Linux/MacOS Installation

1. Install Python (if not installed):
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv

   # MacOS with Homebrew
   brew install python3
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hr-management.git
   ```

3. Create a virtual environment:
   ```bash
   cd hr-management
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```bash
   flask init-db
   ```

6. Run the application:
   ```bash
   flask run
   ```

## Default Credentials

### Admin Login
- Username: admin
- Password: admin123

### Employee Login
- Email: alex.smith@example.com
- Password: emp123

## Project Structure

hr-management/
├── app.py # Main application file

├── database.py # Database configuration

├── schema.sql # Database schema

├── requirements.txt # Python dependencies

├── static/ # Static files (CSS, JS, images)

│ ├── style.css

│ └── profile_pics/ # User profile pictures

├── templates/ # HTML templates

│ ├── admin/ # Admin interface templates

│ └── employee/ # Employee interface templates

└── venv/ # Virtual environment


## Configuration

The application can be configured through environment variables:

bash
Development configuration
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
Production configuration
export FLASK_APP=app.py
export FLASK_ENV=production
export FLASK_DEBUG=0


## Development

1. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/MacOS
   source venv/bin/activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run tests:
   ```bash
   python -m pytest
   ```

## Production Deployment

For production deployment, consider:

1. Using a production WSGI server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 app:app
   ```

2. Setting up a reverse proxy (e.g., Nginx)
3. Using environment variables for sensitive data
4. Implementing proper security measures
5. Regular database backups

## Security Considerations

- All passwords are hashed using MD5 (Note: Consider using stronger hashing in production)
- Session management is implemented
- CSRF protection is enabled
- Input validation is implemented
- File upload restrictions are in place

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please create an issue in the GitHub repository or contact the maintainers.

2.Create a DOCUMENTATION.md file for more detailed technical documentation:

# HR Management System - Technical Documentation

## System Architecture

### Components

1. **Web Application (Flask)**
   - Handles HTTP requests
   - Manages user sessions
   - Renders templates
   - Processes form submissions

2. **Database (SQLite)**
   - Stores user data
   - Manages relationships
   - Handles transactions

3. **File Storage**
   - Manages profile pictures
   - Handles file uploads

### Database Schema

#### Users Table

sql
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


[Continue with other table schemas...]

## API Documentation

### Authentication Endpoints

#### POST /admin/login
Authenticates an admin user.

Request:

json
{
"username": "string",
"password": "string"
}


Response:

json
{
"status": "success",
"message": "Login successful",
"user": {
"id": "integer",
"name": "string",
"role": "admin"
}
}


[Continue with other endpoints...]

## Development Guide

### Setting Up Development Environment

1. **Database Migrations**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

2. **Adding New Features**
   - Create new route in app.py
   - Add template in templates/
   - Update database schema if needed
   - Add tests

### Testing

1. **Unit Tests**
   ```python
   def test_admin_login():
       # Test code here
   ```

2. **Integration Tests**
   ```python
   def test_employee_workflow():
       # Test code here
   ```

## Deployment Guide

### Server Requirements

- 1 CPU core (minimum)
- 2GB RAM (minimum)
- 20GB storage
- Ubuntu 20.04 LTS (recommended)

### Deployment Steps

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update
   sudo apt upgrade

   # Install dependencies
   sudo apt install python3 python3-pip nginx
   ```

2. **Application Setup**
   ```bash
   # Create application directory
   sudo mkdir /var/www/hr-management
   sudo chown -R $USER:$USER /var/www/hr-management

   # Clone repository
   git clone https://github.com/webtech781/hr-management.git
   ```

[Continue with deployment steps...]

## Maintenance Guide

### Backup Procedures

1. **Database Backup**
   ```bash
   # Backup database
   sqlite3 hr_system.db .dump > backup.sql
   ```

2. **File Backup**
   ```bash
   # Backup uploads
   tar -czf uploads_backup.tar.gz static/profile_pics/
   ```

### Monitoring

1. **Application Logs**
   - Location: `/var/log/hr-management/`
   - Rotation: Daily
   - Retention: 30 days

2. **Performance Monitoring**
   - Use Flask-Monitor extension
   - Monitor database queries
   - Track response times

### Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**
   - Check database file permissions
   - Verify connection string
   - Check disk space

2. **File Upload Problems**
   - Verify directory permissions
   - Check file size limits
   - Validate file types

[Continue with more sections as needed...]

