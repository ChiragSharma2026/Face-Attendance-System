# Face Recognition Attendance System

A real-time attendance tracking system using face recognition. Automatically marks students IN and OUT, logs attendance to a local database, and sends email notifications to parents on each event.

---

## Features

- Real-time face detection and recognition via webcam
- Automatic IN / OUT marking with minimum session duration enforcement
- SQLite database for persistent attendance logging
- Automated parent email notifications on arrival and departure
- Daily attendance reset at midnight
- Configurable face matching tolerance and session timeout

---

## How It Works

1. **Face Encoding** — Student photos are stored in the `dataset/` folder. `encode_faces.py` generates 128-dimensional face encodings using dlib and saves them as a pickle file.
2. **Registration** — `register_students.py` adds student records (roll number, name, parent email) to the SQLite database.
3. **Attendance** — `take_attendance.py` runs the webcam feed. Every 15 frames, it runs full face recognition. On a match:
   - First detection → marks IN, sends arrival email
   - After minimum session time (45 min) → marks OUT, sends departure email
   - Between IN and OUT → shows remaining time, blocks early exit logging

---

## Project Structure

```
Face_Attendance_System/
│
├── config.py              # Tolerance, cooldown, timeout settings
├── db.py                  # SQLite database functions
├── email_service.py       # Email notification functions
├── encode_faces.py        # Generate face encodings from dataset
├── register_students.py   # Add students to database
├── take_attendance.py     # Main attendance system (webcam)
├── test_email.py          # Test email configuration
├── requirements.txt
├── run.md                 # Run order
│
├── dataset/               # Add student photos here (one folder per student)
└── encodings/             # Auto-generated face encodings stored here
```

---

## Setup & Installation

### 1. Install Dependencies

> **Note:** `dlib` must be installed manually before `face_recognition`.  
> Download the prebuilt wheel for your Python version from [dlib releases](https://github.com/z-mahmud22/Dlib_Windows_Python3.x).

```bash
pip install dlib-19.22.99-cp310-cp310-win_amd64.whl
pip install -r requirements.txt
```

### 2. Set Environment Variables

This project uses environment variables for email credentials. Set them before running:

**Windows:**
```
setx SENDER_EMAIL "youremail@gmail.com"
setx APP_PASSWORD "your_gmail_app_password"
```

> Use a Gmail App Password, not your actual Gmail password.  
> Generate one at: Google Account → Security → 2-Step Verification → App Passwords

### 3. Add Student Photos

Create a folder inside `dataset/` named after each student. Add 3–5 clear face photos per student.

```
dataset/
├── Chirag/
│   ├── photo1.jpg
│   └── photo2.jpg
└── Aditya/
    ├── photo1.jpg
    └── photo2.jpg
```

### 4. Register Students

Edit `register_students.py` and add student details:

```python
students = [
    ("CS101", "Chirag", "parent_email@gmail.com"),
    ("CS102", "Aditya", "parent_email@gmail.com"),
]
```

---

## Running the System

Run in this order:

```bash
py -3.10 encode_faces.py        # Generate face encodings
py -3.10 register_students.py   # Register students in DB
py -3.10 take_attendance.py     # Start attendance system
```

Press `Q` to quit the webcam window.

---

## Configuration

Edit `config.py` to adjust the system behavior:

| Parameter | Default | Description |
|---|---|---|
| `TOLERANCE` | 0.38 | Face match strictness (lower = stricter) |
| `TIMEOUT_SECONDS` | 3600 | Session timeout (1 hour) |
| `MESSAGE_COOLDOWN` | 10 | Seconds between repeat console messages |

---

## Tech Stack

- Python 3.10
- OpenCV — webcam feed and frame processing
- face_recognition (dlib) — 128-d face encoding and matching
- NumPy — distance calculations
- SQLite — attendance and student data storage
- smtplib — automated email notifications
