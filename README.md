# 🖥️ Smart Lab Fault Reporter

**A Web-Based Computer Laboratory Fault Reporting and Management System**

Smart Lab Fault Reporter is a Flask-based web application designed to simplify the process of reporting, monitoring and managing technical issues in computer laboratories.

The system provides separate access for students and laboratory staff, making fault reporting and issue tracking easier and more organized.

## 🚀 Features

### Student Module
- Student registration and login
- Student dashboard
- Submit computer laboratory fault reports
- Select fault categories
- View previously submitted reports
- Track fault resolution status

### Lab Staff Module
- Lab staff and assistant registration
- Secure staff login
- Staff dashboard
- View and manage fault reports
- Update fault status
- Manage student information
- Monitor laboratory issues

### Additional Features
- Hardware, Software and Network fault categories
- Pending, In Progress and Resolved status tracking
- Activity logging
- Excel backup and restore
- Light and Dark theme support

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML5 | Web page structure |
| CSS3 | Styling and layout |
| JavaScript | Interactive functionality |
| OpenPyXL | Excel backup and restore |

## 📁 Project Structure

```text
Smart-Lab-Fault-Reporter/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── admin.html
│   ├── admin_login.html
│   ├── student_login.html
│   ├── student_dashboard.html
│   ├── staff_register.html
│   └── other HTML files
│
└── static/
    ├── style.css
    ├── buttons.css
    ├── theme.css
    ├── theme.js
    └── other static assets
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jeevabharathp-collab/smart-lab-fault-reporter.git
```

### 2. Open the Project Folder

```bash
cd smart-lab-fault-reporter
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your own secret values:

```env
FLASK_SECRET_KEY=your-secret-key
STAFF_REGISTRATION_CODE=your-private-code
```

**Important:** Never upload your `.env` file or private credentials to GitHub.

### 7. Run the Application

```bash
python app.py
```

### 8. Open in Browser

```text
http://127.0.0.1:5000/
```

## 🎯 Project Objective

The main objective of this project is to provide an organized digital platform for computer laboratory fault reporting and management.

It reduces manual reporting efforts and helps laboratory staff monitor and manage technical issues efficiently.

## 🔮 Future Enhancements

- Email notifications
- Advanced analytics dashboard
- Fault report statistics
- Improved mobile responsiveness
- Deployment on a cloud hosting platform

## 👨‍💻 Developer

**Jeevabharath P.**

Engineering Student | Aspiring Data Analyst | Python Developer

## 📌 Project Status

Developed as an engineering portfolio project.

---

⭐ If you find this project interesting, feel free to explore the repository and its source code.
