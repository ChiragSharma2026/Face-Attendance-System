import smtplib
from email.message import EmailMessage
import os

# ===== CONFIG =====
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
# ==================

def send_test_email(to_email):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Test Email - Attendance System"

    msg.set_content(
        "This is a test email from the Face Attendance System.\n\n"
        "If you received this, email setup is working correctly."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

def send_mark_in_email(to_email, student_name, roll_no, time):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Attendance Update - Arrival"

    msg.set_content(
        f"""
Dear Parent,

This is to inform you that your ward {student_name}
(Roll No: {roll_no}) arrived in class at {time}.

Regards,
Automated Attendance System
        """
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)


def send_mark_out_email(to_email, student_name, roll_no, time):
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = "Attendance Update - Departure"

    msg.set_content(
        f"""
Dear Parent,

This is to inform you that your ward {student_name}
(Roll No: {roll_no}) left the class at {time}.

Regards,
Automated Attendance System
        """
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
