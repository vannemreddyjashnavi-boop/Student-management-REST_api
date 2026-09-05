from flask import Flask, request, jsonify
import sqlite3
from functools import wraps

app = Flask(__name__)

DATABASE = "students.db"
API_KEY = "codomax123"


# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- AUTHENTICATION ----------------

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = request.headers.get("X-API-Key")

        if key != API_KEY:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid or missing API key"
            }), 401

        return f(*args, **kwargs)

    return decorated_function


# ---------------- VALIDATION ----------------

def validate_student(data):
    required_fields = ["name", "email", "course", "year"]

    for field in required_fields:
        if field not in data:
            return f"{field} is required"

    if not isinstance(data["year"], int):
        return "Year must be an integer"

    if data["year"] not in [1, 2, 3, 4]:
        return "Year must be between 1 and 4"

    return None


# ---------------- HOME ----------------

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Student Management REST API",
        "status": "API is running"
    })


# ---------------- GET ALL STUDENTS ----------------

@app.route("/students", methods=["GET"])
@authenticate
def get_students():

    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ---------------- GET SINGLE STUDENT ----------------

@app.route("/students/<int:student_id>", methods=["GET"])
@authenticate
def get_student(student_id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


# ---------------- CREATE STUDENT ----------------

@app.route("/students", methods=["POST"])
@authenticate
def create_student():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body must contain JSON"
        }), 400

    error = validate_student(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    try:
        conn = get_db_connection()

        cursor = conn.execute("""
            INSERT INTO students
            (name, email, course, year)
            VALUES (?, ?, ?, ?)
        """, (
            data["name"],
            data["email"],
            data["course"],
            data["year"]
        ))

        conn.commit()

        student_id = cursor.lastrowid

        conn.close()

        return jsonify({
            "message": "Student created successfully",
            "student_id": student_id
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Email already exists"
        }), 409


# ---------------- UPDATE STUDENT ----------------

@app.route("/students/<int:student_id>", methods=["PUT"])
@authenticate
def update_student(student_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    error = validate_student(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if existing is None:
        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    try:
        conn.execute("""
            UPDATE students
            SET name = ?, email = ?, course = ?, year = ?
            WHERE id = ?
        """, (
            data["name"],
            data["email"],
            data["course"],
            data["year"],
            student_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student updated successfully"
        })

    except sqlite3.IntegrityError:
        conn.close()

        return jsonify({
            "error": "Email already exists"
        }), 409


# ---------------- DELETE STUDENT ----------------

@app.route("/students/<int:student_id>", methods=["DELETE"])
@authenticate
def delete_student(student_id):

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if existing is None:
        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Student deleted successfully"
    })


# ---------------- ERROR HANDLER ----------------

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "error": "Endpoint not found"
    }), 404


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
