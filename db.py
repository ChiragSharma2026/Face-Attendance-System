import sqlite3

DB_FILE = "attendance.db"


# ---------------- CONNECTION ----------------
def get_connection():
    return sqlite3.connect(DB_FILE)


# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            parent_email TEXT NOT NULL
        )
    """)

    # Attendance table (IN / OUT based)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            in_time TEXT,
            out_time TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------- STUDENT FUNCTIONS ----------------
def add_student(student_code, name, parent_email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO students (student_code, name, parent_email) VALUES (?, ?, ?)",
        (student_code, name, parent_email)
    )

    conn.commit()
    conn.close()



def get_student_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, student_code, parent_email FROM students WHERE name = ?",
        (name,)
    )

    result = cursor.fetchone()
    conn.close()

    return result  # (student_id, roll_no, parent_email)



# ---------------- ATTENDANCE FUNCTIONS ----------------
def get_open_attendance(student_id, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, in_time
        FROM attendance
        WHERE student_id = ? AND date = ? AND out_time IS NULL
    """, (student_id, date))

    result = cursor.fetchone()
    conn.close()

    return result  # (attendance_id, in_time) or None


def mark_in(student_id, date, in_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance (student_id, date, in_time)
        VALUES (?, ?, ?)
    """, (student_id, date, in_time))

    conn.commit()
    conn.close()


def mark_out(attendance_id, out_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance
        SET out_time = ?
        WHERE id = ?
    """, (out_time, attendance_id))

    conn.commit()
    conn.close()

def has_attended_today(student_id, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE student_id = ? AND date = ?
    """, (student_id, date))

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0
