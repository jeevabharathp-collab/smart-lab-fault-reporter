
# Smart Lab Fault Reporter

A Flask-based web application designed to simplify computer laboratory fault reporting and management.

## Features

- Student registration and login
- Lab staff and assistant authentication
- Computer lab fault reporting
- Hardware, software and network issue categories
- Fault status tracking
- Staff dashboard
- Student management
- Activity logging
- Excel backup and restore
- Light and dark themes

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- OpenPyXL

## Installation

1. Clone the repository:

   `git clone https://github.com/jeevabharathp-collab/smart-lab-fault-reporter.git`

2. Open the project folder:

   `cd smart-lab-fault-reporter`

3. Create a virtual environment:

   `python -m venv venv`

4. Activate it in Windows PowerShell:

   `.\venv\Scripts\Activate.ps1`

5. Install dependencies:

   `pip install -r requirements.txt`

6. Create a `.env` file with your own secret values:

   `FLASK_SECRET_KEY=your-secret-key`

   `STAFF_REGISTRATION_CODE=your-private-code`

7. Run the application:

   `python app.py`

8. Open `http://127.0.0.1:5000/` in your browser.

## Project Status

Developed as an engineering portfolio project.

## Author

Jeevabharath
