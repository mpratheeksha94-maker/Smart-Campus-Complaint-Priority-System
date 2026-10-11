from flask import Flask, render_template, request, session, redirect, url_for
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from priority import detect_category, detect_department, calculate_priority


app = Flask(__name__)
app.secret_key = "smart-campus-secret-key"


@app.route("/")
def home():
    return "Smart Campus Complaint System is Running!"


# Student Registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash password before storing it
        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'student')
        """

        cursor.execute(query, (name, email, hashed_password))
        connection.commit()

        cursor.close()
        connection.close()

        return "Registration successful!"

    return render_template("register.html")

# Student Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            session["role"] = user["role"]

            # Admin goes to Admin Dashboard
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))

            # Student goes to Student Dashboard
            return redirect(url_for("student_dashboard"))

        return "Invalid email or password!"

    return render_template("login.html")


# Student Dashboard
@app.route("/student-dashboard")
def student_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "student_dashboard.html",
        name=session["user_name"]
    )
    # Admin Dashboard
# Admin Dashboard
@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        return redirect(url_for("student_dashboard"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get all complaints
    query = """
        SELECT
            c.complaint_id,
            c.title,
            c.category,
            c.location,
            c.priority_score,
            c.priority_level,
            c.status,
            d.department_name
        FROM complaints c
        LEFT JOIN departments d
            ON c.department_id = d.department_id
        ORDER BY c.created_at DESC
    """

    cursor.execute(query)

    complaints = cursor.fetchall()

    # Dashboard counts
    total_complaints = len(complaints)

    high_priority = sum(
        1 for c in complaints
        if c["priority_level"] == "High"
    )

    pending = sum(
        1 for c in complaints
        if c["status"] == "Pending"
    )

    resolved = sum(
        1 for c in complaints
        if c["status"] == "Resolved"
    )

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        name=session["user_name"],
        complaints=complaints,
        total_complaints=total_complaints,
        high_priority=high_priority,
        pending=pending,
        resolved=resolved
    )


# Submit Complaint
@app.route("/submit-complaint", methods=["GET", "POST"])
def submit_complaint():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        urgency = int(request.form["urgency"])

        # Detect category
        category = detect_category(title + " " + description)

        # Detect department
        department_name = detect_department(category)

        # Default values
        affected_students = 1
        location_importance = 5
        complaint_frequency = 1

        # Calculate priority
        priority_score, priority_level = calculate_priority(
            urgency,
            affected_students,
            location_importance,
            complaint_frequency
        )

        # Connect to database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Find department ID
        cursor.execute(
            "SELECT department_id FROM departments WHERE department_name = %s",
            (department_name,)
        )

        department = cursor.fetchone()
        department_id = department[0] if department else None

        # Insert complaint
        query = """
            INSERT INTO complaints
            (
                user_id,
                title,
                description,
                location,
                urgency,
                category,
                department_id,
                affected_students,
                location_importance,
                complaint_frequency,
                priority_score,
                priority_level
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (
                session["user_id"],
                title,
                description,
                location,
                urgency,
                category,
                department_id,
                affected_students,
                location_importance,
                complaint_frequency,
                priority_score,
                priority_level
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return "Complaint submitted successfully!"

    return render_template("submit_complaint.html")

# My Complaints
@app.route("/my-complaints")
def my_complaints():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            c.complaint_id,
            c.title,
            c.description,
            c.category,
            c.location,
            c.priority_score,
            c.priority_level,
            c.status,
            c.created_at,
            d.department_name
        FROM complaints c
        LEFT JOIN departments d
            ON c.department_id = d.department_id
        WHERE c.user_id = %s
        ORDER BY c.created_at DESC
    """

    cursor.execute(query, (session["user_id"],))

    complaints = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "my_complaints.html",
        complaints=complaints,
        name=session["user_name"]
    )
# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)