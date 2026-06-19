from flask import Flask, request, session, redirect, send_from_directory
import sqlite3
import os
print("DB Path:", os.path.abspath("complaints.db"))
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

app = Flask(__name__)
app.secret_key = "campus_secret"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_EMAIL = "mycollegeadmin@gmail.com"
ADMIN_PASSWORD = "@admin123"

print("GMAIL_EMAIL =", GMAIL_EMAIL)
print("GMAIL_APP_PASSWORD =", GMAIL_APP_PASSWORD)
def send_email_notification(student, title, category):

    print("EMAIL FUNCTION CALLED")

    try:

        print("GMAIL_EMAIL =", GMAIL_EMAIL)
        print("APP PASSWORD =", GMAIL_APP_PASSWORD)

        import socket

        try:
            print("SMTP IP =", socket.gethostbyname("smtp.gmail.com"))
        except Exception as e:
            print("DNS ERROR:", e)

        msg = MIMEMultipart()

        msg["From"] = GMAIL_EMAIL
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = "New Campus Complaint"

        APP_URL = "https://campus-problem-detective--1.onrender.com"

        body = f"""
New Complaint Submitted

Student: {student}
Title: {title}
Category: {category}

Open Admin Dashboard:
{APP_URL}/admin-login
"""

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()

        server.login(
            GMAIL_EMAIL,
            GMAIL_APP_PASSWORD
        )

        server.send_message(msg)
        server.quit()

    except Exception as e:
        import traceback
        print("Email Error:", str(e))
        traceback.print_exc()
# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect("complaints.db", timeout=20)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        regno TEXT,
        title TEXT,
        category TEXT,
        description TEXT,
        photo TEXT,
        location TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    cur.execute("""
CREATE TABLE IF NOT EXISTS notifications(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    complaint_id INTEGER
)
""")

    conn.commit()
    conn.close()

init_db()

# ================= HOME PAGE =================

@app.route("/")
def home():

    return """
    <html>

    <head>

    <title>Campus Problem Detective</title>

    <style>

    body{
        margin:0;
        font-family:Arial;
        background:linear-gradient(
        135deg,
        #0f2027,
        #203a43,
        #2c5364
        );
    }

    .container{
        width:400px;
        margin:80px auto;
        background:white;
        padding:30px;
        border-radius:15px;
        text-align:center;
        box-shadow:0 0 20px rgba(0,0,0,.3);
    }

    h1{
        color:#2c3e50;
    }

    a{
        display:block;
        margin:12px;
        padding:12px;
        text-decoration:none;
        color:white;
        border-radius:8px;
    }

    .student{
        background:#3498db;
    }

    .admin{
        background:#e67e22;
    }

    .view{
        background:#2ecc71;
    }

    </style>

    </head>

    <body>

    <div class="container">

        <h1>🏫 Campus Problem Detective</h1>

        <a class="student"
        href="/student-login">
        🎓 Student Login
        </a>

        <a class="admin"
        href="/admin-login">
        👨‍💼 Admin Login
        </a>

        <a class="view"
        href="/view-complaints">
        📋 View Complaints
        </a>

    </div>

    </body>

    </html>
    """

# ================= STUDENT LOGIN =================

@app.route("/student-login", methods=["GET", "POST"])
def student_login():

    # Already login ಇದ್ದರೆ dashboard open
    if session.get("student_reg"):
        return redirect("/student-dashboard")

    if request.method == "POST":

        session["student_name"] = request.form["name"]
        session["student_reg"] = request.form["regno"]

        return redirect("/student-dashboard")

    return """

    <html>

    <style>

    body{
        background:#ecf0f1;
        font-family:Arial;
    }

    .box{
        width:350px;
        margin:80px auto;
        background:white;
        padding:25px;
        border-radius:12px;
    }

    input{
        width:100%;
        padding:10px;
        margin:8px 0;
    }

    button{
        width:100%;
        padding:10px;
        background:#3498db;
        color:white;
        border:none;
        cursor:pointer;
    }

    </style>

    <body>

    <div class="box">

    <h2>🎓 Student Login</h2>

    <form method="post">

    <input
    name="name"
    placeholder="Student Name"
    required>

    <input
    name="regno"
    placeholder="Registration Number"
    required>

    <button>
    Login
    </button>

    </form>

    </div>

    </body>

    </html>

    """

# ================= STUDENT LOGOUT =================

@app.route("/student-logout")
def student_logout():

    session.pop("student_name", None)
    session.pop("student_reg", None)

    return redirect("/")
    # ================= STUDENT DASHBOARD =================

@app.route("/student-dashboard")
def student_dashboard():

    if not session.get("student_reg"):
        return redirect("/student-login")

    return f"""

    <html>

    <style>

    body{{
        font-family:Arial;
        background:#f2f2f2;
    }}

    .box{{
        width:500px;
        margin:auto;
        margin-top:40px;
        background:white;
        padding:25px;
        border-radius:12px;
        box-shadow:0 0 10px #ccc;
    }}

    input,
    textarea,
    select{{
        width:100%;
        padding:10px;
        margin-top:10px;
        margin-bottom:10px;
    }}

    button{{
        background:#27ae60;
        color:white;
        border:none;
        padding:12px;
        width:100%;
        cursor:pointer;
    }}

    .logout{{
        background:red;
        color:white;
        padding:10px 15px;
        text-decoration:none;
        border-radius:5px;
    }}

    </style>

    <body>

    <div class="box">

    <a class="logout"
    href="/student-logout">
    Logout
    </a>
    
    <a class="logout" href="/">
🏠 Home
</a>

    <h2>
    🎓 Welcome {session['student_name']}
    </h2>

    <form
    action="/submit"
    method="post"
    enctype="multipart/form-data">

    <input
    name="title"
    placeholder="Problem Title"
    required>

    <select name="category">

    <option>Water Problem</option>

    <option>Electricity</option>

    <option>Classroom</option>

    <option>Road Damage</option>

    <option>Cleaning</option>

    <option>Other</option>

    </select>

    <textarea
    name="description"
    rows="5"
    placeholder="Describe the problem"
    required></textarea>

    <input
    type="file"
    name="photo">

    <button>
    Submit Complaint
    </button>

    </form>

    </div>

    </body>

    </html>

    """

# ================= SUBMIT COMPLAINT =================

@app.route("/submit", methods=["POST"])
def submit():

    if not session.get("student_reg"):
        return redirect("/student-login")

    filename = ""

    photo = request.files.get("photo")

    if photo and photo.filename:

        filename = secure_filename(photo.filename)

        photo.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    cur.execute(
    """
    INSERT INTO complaints
    (
    student_name,
    regno,
    title,
    category,
    description,
    photo,
    location,
    status
    )
    VALUES(?,?,?,?,?,?,?,?)
    """,
    (
    session.get("student_name"),
    session.get("student_reg"),
    request.form["title"],
    request.form["category"],
    request.form["description"],
    filename,
    "GPS Not Available",
    "Pending"
    )
    )
    complaint_id = cur.lastrowid
    # Notification for admin

    cur.execute(
"""
INSERT INTO notifications(message, complaint_id)
VALUES(?,?)
""",
(
f"New complaint submitted by {session.get('student_name')}",
complaint_id
)
)

    send_email_notification(
    session.get("student_name"),
    request.form["title"],
    request.form["category"]
)

    conn.commit()
    conn.close()

    return """

    <html>

    <style>

    body{
        background:#eafaf1;
        text-align:center;
        font-family:Arial;
        padding-top:120px;
    }

    .btn{
        background:#27ae60;
        color:white;
        padding:12px 25px;
        text-decoration:none;
        border-radius:8px;
    }

    </style>

    <h1>
    ✅ Complaint Submitted Successfully
    </h1>

    <br><br>

    <a class="btn"
    href="/student-dashboard">
    Submit Another Complaint
    </a>

    <br><br>

    <a class="btn"
    href="/">
    Home
    </a>

    </html>

    """
    # ================= UPLOAD IMAGE VIEW =================

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )

# ================= VIEW COMPLAINTS =================

@app.route("/view-complaints")
def view_complaints():

    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    rows = cur.execute(
    """
    SELECT
        id,
        student_name,
        title,
        category,
        status
    FROM complaints
    ORDER BY id DESC
    """
    ).fetchall()

    conn.close()

    html = """

    <html>

    <style>

    body{
        font-family:Arial;
        background:#f2f2f2;
    }

    .box{
        width:800px;
        margin:auto;
        background:white;
        padding:20px;
        margin-top:20px;
        border-radius:10px;
    }

    .card{
        border:1px solid #ddd;
        padding:15px;
        margin:10px;
        border-radius:10px;
        background:#fafafa;
    }

    .pending{
        color:#e67e22;
        font-weight:bold;
    }

    .solved{
        color:green;
        font-weight:bold;
    }

    </style>

    <body>

    <div class='box'>

    <h1>📋 Complaints List</h1>

    """

    if not rows:

        html += """
        <h3>No complaints found.</h3>
        """

    for r in rows:

        status_class = "pending"

        if r[4] == "Solved":
            status_class = "solved"

        html += f"""

        <div class='card'>

        <b>ID:</b> {r[0]} <br><br>

        <b>Student:</b> {r[1]} <br><br>

        <b>Title:</b> {r[2]} <br><br>

        <b>Category:</b> {r[3]} <br><br>

        <b>Status:</b>

        <span class="{status_class}">
        {r[4]}
        </span>

        </div>

        """

    html += """

    <br>

    <a href="/">
    🏠 Back To Home
    </a>

    </div>

    </body>

    </html>

    """

    return html
    # ================= ADMIN LOGIN =================

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    # Already login ಇದ್ದರೆ direct dashboard
    if session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect("/admin")

        return """
        <h2 style='color:red;text-align:center;'>
        Invalid Email or Password
        </h2>
        <center>
        <a href='/admin-login'>Try Again</a>
        </center>
        """

    return """

    <html>

    <style>

    body{
        background:#f5f5f5;
        font-family:Arial;
    }

    .box{
        width:350px;
        margin:80px auto;
        background:white;
        padding:25px;
        border-radius:12px;
        box-shadow:0 0 10px #ccc;
    }

    input{
        width:100%;
        padding:10px;
        margin:8px 0;
    }

    button{
        width:100%;
        padding:10px;
        background:#e67e22;
        color:white;
        border:none;
        cursor:pointer;
    }

    </style>

    <body>

    <div class="box">

    <h2>👨‍💼 Admin Login</h2>

    <form method="post">

    <input
    type="email"
    name="email"
    placeholder="Email"
    required>

    <input
    type="password"
    name="password"
    placeholder="Password"
    required>

    <button>
    Login
    </button>

    </form>

    </div>

    </body>

    </html>

    """

# ================= ADMIN DASHBOARD =================

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    rows = cur.execute(
    """
    SELECT *
    FROM complaints
    ORDER BY id DESC
    """
    ).fetchall()

    notifications = cur.execute(
    """
    SELECT message
    FROM notifications
    ORDER BY id DESC
    LIMIT 10
    """
    ).fetchall()

    pending_count = cur.execute(
    """
    SELECT COUNT(*)
    FROM complaints
    WHERE status='Pending'
    """
    ).fetchone()[0]

    conn.close()

    html = f"""

    <html>

    <style>

    body{{
        font-family:Arial;
        background:#ecf0f1;
    }}

    .container{{
        width:900px;
        margin:auto;
        margin-top:20px;
    }}

    .card{{
        background:white;
        padding:15px;
        margin-bottom:15px;
        border-radius:10px;
        box-shadow:0 0 5px #ccc;
    }}

    .btn{{
        background:#27ae60;
        color:white;
        padding:8px 12px;
        text-decoration:none;
        border-radius:5px;
    }}

    .delete{{
        background:red;
        color:white;
        padding:8px 12px;
        text-decoration:none;
        border-radius:5px;
    }}

    .logout{{
        background:#c0392b;
        color:white;
        padding:10px;
        text-decoration:none;
        border-radius:5px;
    }}

    .notify{{
        background:#f39c12;
        color:white;
        padding:15px;
        border-radius:10px;
        margin-bottom:20px;
    }}

    </style>

    <body>

    <div class="container">

    <h1>👨‍💼 Admin Dashboard</h1>

    <a class="logout"
    href="/logout">
    Logout
    </a>

<a class="logout" href="/">
🏠 Home
</a>
    <br><br>

    <div class="notify">
    🔔 Pending Complaints : {pending_count}
    </div>

    <h2>Latest Notifications</h2>

    """

    for n in notifications:

        html += f"""
        <div class='card'>
        {n[0]}
        </div>
        """

    html += "<h2>All Complaints</h2>"

    for r in rows:

        photo_html = ""

        if r[6]:
            photo_html = f"""
            <img
            src="/uploads/{r[6]}"
            width="250">
            <br><br>
            """

        html += f"""

        <div class="card">

        <b>ID:</b> {r[0]} <br><br>

        <b>Name:</b> {r[1]} <br><br>

        <b>Reg No:</b> {r[2]} <br><br>

        <b>Title:</b> {r[3]} <br><br>

        <b>Category:</b> {r[4]} <br><br>

        <b>Description:</b> {r[5]} <br><br>

        {photo_html}

        <b>Location:</b> {r[7]} <br><br>

        <b>Status:</b> {r[8]} <br><br>

        <a class="btn"
        href="/mark-solved/{r[0]}">
        Mark Solved
        </a>

        &nbsp;

        <a class="delete"
        href="/delete/{r[0]}"
        onclick="return confirm('Delete Complaint?')">
        Delete
        </a>

        </div>

        """

    html += """
    </div>
    </body>
    </html>
    """

    return html
    # ================= DELETE COMPLAINT =================

@app.route("/delete/<int:id>")
def delete_complaint(id):

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    # photo file delete (optional)
    row = cur.execute(
        "SELECT photo FROM complaints WHERE id=?",
        (id,)
    ).fetchone()

    if row and row[0]:

        photo_path = os.path.join(
            UPLOAD_FOLDER,
            row[0]
        )

        if os.path.exists(photo_path):
            os.remove(photo_path)

    cur.execute(
        "DELETE FROM complaints WHERE id=?",
        (id,)
    )
    cur.execute(
    "DELETE FROM notifications WHERE complaint_id=?",
    (id,)
)

    conn.commit()
    conn.close()

    return redirect("/admin")


# ================= MARK SOLVED =================

@app.route("/mark-solved/<int:id>")
def mark_solved(id):

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE complaints
        SET status='Solved'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ================= ADMIN LOGOUT =================

# ================= CLEAR NOTIFICATIONS =================

@app.route("/clear-notifications")
def clear_notifications():

    conn = sqlite3.connect("complaints.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM notifications")

    conn.commit()
    conn.close()

    return "All notifications deleted"
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ================= RUN APP =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
)
