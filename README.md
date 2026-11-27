# Smart Lab Fault Reporter

**A Web-Based Computer Laboratory Fault Reporting and Management System**

Smart Lab Fault Reporter is a Flask-based web application designed to simplify the process of reporting, tracking, and managing technical issues in computer laboratories.

The application provides separate access for students and laboratory staff, helping organize fault reports and monitor their resolution status.

## Features

### Student Module
- Student registration and login
- Student dashboard
- Submit laboratory fault reports
- View and track reported issues

### Lab Staff and Admin Module
- Lab staff registration and login
- Admin dashboard
- View and manage student details
- View submitted fault reports
- Update fault report status
- Database backup and restore

### Technical Features
- Flask-based web application
- SQLite database
- Password hashing and session-based authentication
- Excel workbook support
- Environment-based configuration

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- OpenPyXL
- python-dotenv

## Project Structure

```text
smart-lab-fault-reporter/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── HTML pages
│
└── static/
    ├── buttons.css
    ├── style.css
    ├── theme.css
    └── theme.js
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/jeevabharathp-collab/smart-lab-fault-reporter.git
cd smart-lab-fault-reporter
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=replace_with_your_own_secret
STAFF_REGISTRATION_CODE=replace_with_your_own_code
```

Use your own private values. Never publish your actual secret key or registration code.

### 6. Run the application

```bash
python app.py
```

Open the application in your browser:

http://127.0.0.1:5000/

## Security Notes

- Keep `.env` private.
- Do not upload your local database or virtual environment.
- Use the staff registration code only for authorized laboratory staff.

## Project Status

Developed as an engineering portfolio project.

## Author

**Jeevabharath P**

Engineering Student | Aspiring Data Analyst | Python Developer