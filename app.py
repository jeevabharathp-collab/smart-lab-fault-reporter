from io import BytesIO
from flask import send_file
from openpyxl import Workbook, load_workbook
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from functools import wraps
import os
from dotenv import load_dotenv

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash


# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "lab_faults.db"

STAFF_REGISTRATION_CODE = os.getenv("STAFF_REGISTRATION_CODE")
if not STAFF_REGISTRATION_CODE:
    raise RuntimeError("STAFF_REGISTRATION_CODE is missing from .env")

# --------------------------------------------------
# 2. DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# --------------------------------------------------
# 3. CREATE DATABASE TABLES
# --------------------------------------------------

def create_table():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Student table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            student_name TEXT NOT NULL,
            department TEXT NOT NULL,
            year TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Add register_number to an existing students table
    student_columns = [
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(students)"
        ).fetchall()
    ]

    if "register_number" not in student_columns:
        cursor.execute("""
            ALTER TABLE students
            ADD COLUMN register_number TEXT
        """)

    # Lab staff table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lab_staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_username TEXT UNIQUE NOT NULL,
            staff_name TEXT NOT NULL,
            department TEXT NOT NULL,
            staff_code TEXT NOT NULL,
            staff_role TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Fault reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fault_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            lab_name TEXT NOT NULL,
            computer_number TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
    """)

    # Add student_id to an existing fault_reports table
    report_columns = [
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(fault_reports)"
        ).fetchall()
    ]

    if "student_id" not in report_columns:
        cursor.execute("""
            ALTER TABLE fault_reports
            ADD COLUMN student_id TEXT
        """)

    connection.commit()
    connection.close()


# --------------------------------------------------
# 4. LOGIN PROTECTION
# --------------------------------------------------

def student_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "student_username" not in session:
            flash("Please log in as a student.")
            return redirect(url_for("student_login"))

        return function(*args, **kwargs)

    return wrapper


def staff_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "staff_username" not in session:
            flash("Please log in as lab staff.")
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# 5. HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")
app.add_url_rule("/", endpoint="index", view_func=home)



# --------------------------------------------------
# 6. STUDENT REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        student_name = request.form.get("student_name", "").strip()
        department = request.form.get("department", "").strip().lower()
        joining_year = request.form.get("joining_year", "").strip()
        register_number = request.form.get("register_number", "").strip()
        password = request.form.get("password", "")

        if not all([
            username, student_name, department,
            joining_year, register_number, password
        ]):
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        if not re.fullmatch(r"\d{4}", joining_year):
            flash("Enter a valid four-digit joining year.", "error")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[a-zA-Z]+", department):
            flash("Enter a valid department.", "error")
            return redirect(url_for("register"))

        if not re.fullmatch(r"\d{1,4}", register_number):
            flash("Enter a valid register number.", "error")
            return redirect(url_for("register"))

        expected_password = (
            joining_year[-2:] + department + "0" + register_number
        ).lower()

        if len(expected_password) not in (8, 9):
            flash("Password format must contain 8 or 9 characters.", "error")
            return redirect(url_for("register"))

        if password.lower() != expected_password:
            flash("Password does not match the required format.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO students (
                    student_id,
                    student_name,
                    department,
                    year,
                    register_number,
                    password
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                username,
                student_name,
                department,
                joining_year,
                register_number,
                hashed_password
            ))

            connection.commit()

            flash(
                "Registration Successful! Your student account has been created.",
                "success"
            )

        except sqlite3.IntegrityError:
            flash("This username is already registered.", "error")

        finally:
            connection.close()

        return redirect(url_for("register"))

    return render_template("register.html")

def student_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            request.form.get("student_id", "")
        ).strip()

        password = request.form.get("password", "")

        connection = get_db_connection()

        student = connection.execute("""
            SELECT * FROM students
            WHERE student_id = ?
        """, (username,)).fetchone()

        connection.close()

        if student and check_password_hash(
            student["password"], password
        ):

            session.clear()
            session["student_username"] = student["student_id"]
            session["student_name"] = student["student_name"]

            return redirect(url_for("student_dashboard"))

        flash("Invalid student username or password.")

    return render_template("student_login.html")
# ---------------------------------------------------
# 7.STUDENT LOGIN
# ----------------------------------------------------

# --------------------------------------------------
# 7. STUDENT LOGIN
# --------------------------------------------------

@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            request.form.get("student_id", "")
        ).strip()

        password = request.form.get("password", "")

        connection = get_db_connection()

        student = connection.execute("""
            SELECT * FROM students
            WHERE student_id = ?
        """, (username,)).fetchone()

        connection.close()

        if student and check_password_hash(
            student["password"], password
        ):

            session.clear()
            session["student_username"] = student["student_id"]
            session["student_name"] = student["student_name"]

            return redirect(url_for("student_dashboard"))

        flash("Invalid student username or password.", "error")

    return render_template("student_login.html")

# --------------------------------------------------
# 8. STUDENT DASHBOARD
# --------------------------------------------------

@app.route("/student_dashboard")
@student_required
def student_dashboard():

    username = session["student_username"]

    connection = get_db_connection()

    student = connection.execute("""
        SELECT * FROM students
        WHERE student_id = ?
    """, (username,)).fetchone()

    reports = connection.execute("""
        SELECT * FROM fault_reports
        WHERE student_id = ?
        ORDER BY id DESC
    """, (username,)).fetchall()

    connection.close()

    return render_template(
        "student_dashboard.html",
        student=student,
        reports=reports
    )


# --------------------------------------------------
# 9. REPORT A LAB FAULT
# --------------------------------------------------

@app.route("/report", methods=["GET", "POST"])
@student_required
def report():

    if request.method == "POST":

        lab_name = request.form.get(
            "lab_name", ""
        ).strip()

        computer_number = request.form.get(
            "computer_number", ""
        ).strip()

        category = request.form.get(
            "category", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        if not all([
            lab_name,
            computer_number,
            category,
            description
        ]):
            flash("Please complete all report fields.")
            return redirect(url_for("report"))

        allowed_categories = [
            "Hardware",
            "Software",
            "Network"
        ]

        if category not in allowed_categories:
            flash("Please select a valid fault category.")
            return redirect(url_for("report"))

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO fault_reports (
                student_id,
                lab_name,
                computer_number,
                category,
                description,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session["student_username"],
            lab_name,
            computer_number,
            category,
            description,
            "Pending",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        connection.close()

        flash("Your fault report was submitted successfully.")

        return redirect(url_for("student_dashboard"))

    return render_template("report.html")


# --------------------------------------------------
# 10. STAFF REGISTRATION
# --------------------------------------------------

@app.route("/staff_register", methods=["GET", "POST"])
def staff_register():

    if request.method == "POST":

        registration_code = request.form.get(
            "registration_code", ""
        ).strip()

        staff_username = request.form.get(
            "staff_username", ""
        ).strip()

        staff_name = request.form.get(
            "staff_name", ""
        ).strip()

        department = request.form.get(
            "department", ""
        ).strip().lower()

        staff_code = request.form.get(
            "staff_code", ""
        ).strip()

        staff_role = request.form.get(
            "staff_role", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not all([
            registration_code,
            staff_username,
            staff_name,
            department,
            staff_code,
            staff_role,
            password,
            confirm_password
        ]):
            flash("Please fill in all fields.")
            return redirect(url_for("staff_register"))

        # Check private registration code
        if registration_code != STAFF_REGISTRATION_CODE:
            flash("Invalid staff registration code.")
            return redirect(url_for("staff_register"))

        # Only these two roles are allowed
        if staff_role not in ["lab staff", "lab assistant"]:
            flash("Only Lab Staff and Lab Assistant can register.")
            return redirect(url_for("staff_register"))

        if not re.fullmatch(r"[a-zA-Z]+", department):
            flash("Enter a valid department.")
            return redirect(url_for("staff_register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("staff_register"))

        # Example: admin@cse040
        expected_password = (
            "admin@" + department + staff_code
        ).lower()

        if password.lower() != expected_password:
            flash(
                "Password must match the required staff password format."
            )
            return redirect(url_for("staff_register"))

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute("""
                INSERT INTO lab_staff (
                    staff_username,
                    staff_name,
                    department,
                    staff_code,
                    staff_role,
                    password,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                staff_username,
                staff_name,
                department,
                staff_code,
                staff_role,
                hashed_password,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            connection.commit()

            flash("Staff registration successful!")
            return redirect(url_for("admin_login"))

        except sqlite3.IntegrityError:
            flash("This staff username is already registered.")

        finally:
            connection.close()

    return render_template("staff_register.html")

# --------------------------------------------------
# EXCEL BACKUP AND RESTORE ACCESS
# Only Lab Staff can use these operations.
# --------------------------------------------------

def lab_staff_admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "staff_username" not in session:
            flash("Please log in as lab staff.", "error")
            return redirect(url_for("admin_login"))

        if session.get("staff_role", "").strip().lower() != "lab staff":
            flash("Only Lab Staff can access backup and restore.", "error")
            return redirect(url_for("admin"))

        return function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# EXCEL BACKUP
# --------------------------------------------------

@app.route("/admin/backup")
@lab_staff_admin_required
def backup_database():

    tables = ["students", "lab_staff", "fault_reports"]

    connection = get_db_connection()

    workbook = Workbook()
    workbook.remove(workbook.active)

    try:
        for table in tables:

            worksheet = workbook.create_sheet(title=table.title())

            columns = [
                row["name"]
                for row in connection.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall()
            ]

            worksheet.append(columns)

            records = connection.execute(
                f"SELECT * FROM {table}"
            ).fetchall()

            for record in records:
                values = [record[column] for column in columns]
                worksheet.append(values)

                # Store all values as text where appropriate.
                # This prevents text beginning with "=" becoming a formula.
                for cell in worksheet[worksheet.max_row]:
                    if isinstance(cell.value, str):
                        cell.data_type = "s"

            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

        output = BytesIO()
        workbook.save(output)
        output.seek(0)

    finally:
        connection.close()

    filename = "SmartLab_Backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# --------------------------------------------------
# EXCEL RESTORE
# Safely merges records; does not delete existing data.
# --------------------------------------------------

@app.route("/admin/restore", methods=["POST"])
@lab_staff_admin_required
def restore_database():

    uploaded_file = request.files.get("backup_file")

    if not uploaded_file or uploaded_file.filename == "":
        flash("Please select an Excel backup file.", "error")
        return redirect(url_for("admin"))

    if not uploaded_file.filename.lower().endswith(".xlsx"):
        flash("Only .xlsx Excel backup files are accepted.", "error")
        return redirect(url_for("admin"))

    try:
        workbook = load_workbook(
            uploaded_file,
            read_only=True,
            data_only=True
        )

        required_sheets = {
            "Students": "students",
            "Lab_Staff": "lab_staff",
            "Fault_Reports": "fault_reports"
        }

        if set(workbook.sheetnames) != set(required_sheets.keys()):
            raise ValueError("The workbook does not contain the required SmartLab sheets.")

        connection = get_db_connection()
        restored_count = 0
        skipped_count = 0

        try:
            connection.execute("BEGIN")

            for sheet_name, table in required_sheets.items():

                worksheet = workbook[sheet_name]

                expected_columns = [
                    row["name"]
                    for row in connection.execute(
                        f"PRAGMA table_info({table})"
                    ).fetchall()
                ]

                headers = [
                    cell.value
                    for cell in next(
                        worksheet.iter_rows(min_row=1, max_row=1)
                    )
                ]

                if headers != expected_columns:
                    raise ValueError(
                        f"Column headings in {sheet_name} do not match the current database."
                    )

                placeholders = ", ".join(["?"] * len(expected_columns))
                column_names = ", ".join(
                    '"' + column.replace('"', '""') + '"'
                    for column in expected_columns
                )

                sql = (
                    f"INSERT OR IGNORE INTO {table} "
                    f"({column_names}) VALUES ({placeholders})"
                )

                for row in worksheet.iter_rows(min_row=2, values_only=False):

                    if all(cell.value is None for cell in row):
                        continue

                    if any(cell.data_type == "f" for cell in row):
                        raise ValueError(
                            f"Formula cells are not allowed in {sheet_name}."
                        )

                    values = [cell.value for cell in row]

                    cursor = connection.execute(sql, values)

                    if cursor.rowcount == 1:
                        restored_count += 1
                    else:
                        skipped_count += 1

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()
            workbook.close()

        flash(
            f"Restore completed! {restored_count} records added; "
            f"{skipped_count} duplicate records skipped. "
            "Existing records were not deleted.",
            "success"
        )

    except Exception as error:
        flash(f"Restore failed: {error}", "error")

    return redirect(url_for("admin"))



# --------------------------------------------------
# 11. STAFF LOGIN / ADMIN LOGIN
# --------------------------------------------------

@app.route("/staff_login", methods=["GET", "POST"])
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        staff_username = request.form.get(
            "staff_username",
            request.form.get("username", "")
        ).strip()

        password = request.form.get("password", "")

        connection = get_db_connection()

        staff = connection.execute("""
            SELECT * FROM lab_staff
            WHERE staff_username = ?
        """, (staff_username,)).fetchone()

        connection.close()

        if staff and check_password_hash(
            staff["password"], password
        ):

            session.clear()
            session["staff_username"] = staff["staff_username"]
            session["staff_name"] = staff["staff_name"]
            session["staff_role"] = staff["staff_role"]

            return redirect(url_for("admin"))

        flash("Invalid staff username or password.")

    return render_template("admin_login.html")


# --------------------------------------------------
# 12. STAFF DASHBOARD
# --------------------------------------------------

@app.route("/admin")
@staff_required
def admin():

    connection = get_db_connection()

    total_reports = connection.execute(
        "SELECT COUNT(*) FROM fault_reports"
    ).fetchone()[0]

    pending_reports = connection.execute(
        "SELECT COUNT(*) FROM fault_reports WHERE status = 'Pending'"
    ).fetchone()[0]

    in_progress_reports = connection.execute(
        "SELECT COUNT(*) FROM fault_reports WHERE status = 'In Progress'"
    ).fetchone()[0]

    resolved_reports = connection.execute(
        "SELECT COUNT(*) FROM fault_reports WHERE status = 'Resolved'"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "admin.html",
        total_reports=total_reports,
        pending_reports=pending_reports,
        in_progress_reports=in_progress_reports,
        resolved_reports=resolved_reports
    )

# --------------------------------------------------
# STUDENT MANAGEMENT
# --------------------------------------------------

@app.route("/students")
@staff_required
def students():

    connection = get_db_connection()

    all_students = connection.execute("""
        SELECT
            student_id,
            student_name,
            register_number,
            department,
            year
        FROM students
        ORDER BY student_name ASC
    """).fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=all_students
    )

# --------------------------------------------------
# VIEW STUDENT DETAILS
# --------------------------------------------------

@app.route("/student_details/<student_id>")
@staff_required
def student_details(student_id):

    connection = get_db_connection()

    student = connection.execute("""
        SELECT
            student_id,
            student_name,
            register_number,
            department,
            year
        FROM students
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    connection.close()

    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    return render_template(
        "student_details.html",
        student=student
    )


# --------------------------------------------------
# DELETE STUDENT
# --------------------------------------------------

@app.route("/delete_student/<student_id>", methods=["POST"])
@staff_required
def delete_student(student_id):

    connection = get_db_connection()

    student = connection.execute("""
        SELECT student_id
        FROM students
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    if student is None:
        connection.close()
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    report_count = connection.execute("""
        SELECT COUNT(*)
        FROM fault_reports
        WHERE student_id = ?
    """, (student_id,)).fetchone()[0]

    if report_count > 0:
        connection.close()
        flash(
            "This student cannot be deleted because fault reports are linked to this account.",
            "error"
        )
        return redirect(url_for("students"))

    connection.execute("""
        DELETE FROM students
        WHERE student_id = ?
    """, (student_id,))

    connection.commit()
    connection.close()

    flash("Student account deleted successfully.", "success")
    return redirect(url_for("students"))


# --------------------------------------------------
# 13. VIEW ALL FAULT REPORTS
# --------------------------------------------------

@app.route("/reports")
@staff_required
def reports():

    connection = get_db_connection()

    all_reports = connection.execute("""
        SELECT
            fault_reports.*,
            students.student_name,
            students.register_number,
            students.department,
            students.student_id AS student_username
        FROM fault_reports
        LEFT JOIN students
        ON fault_reports.student_id = students.student_id
        ORDER BY fault_reports.id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "reports.html",
        reports=all_reports
    )


# --------------------------------------------------
# 14. UPDATE REPORT STATUS
# --------------------------------------------------

@app.route("/update_status/<int:report_id>", methods=["POST"])
@staff_required
def update_status(report_id):

    new_status = request.form.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid report status.")
        return redirect(url_for("reports"))

    connection = get_db_connection()

    connection.execute("""
        UPDATE fault_reports
        SET status = ?
        WHERE id = ?
    """, (new_status, report_id))

    connection.commit()
    connection.close()

    flash("Report status updated successfully.")

    return redirect(url_for("reports"))


# --------------------------------------------------
# 15. LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have logged out successfully.")

    return redirect(url_for("home"))


# --------------------------------------------------
# 16. RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    create_table()

    app.run(debug=True)
