import cv2
import face_recognition
import pickle
import numpy as np
from datetime import datetime
import db
import config
from email_service import send_mark_in_email, send_mark_out_email

# ---------------- CONFIG ----------------
ENCODINGS_FILE = "encodings/face_encodings.pkl"
MIN_OUT_SECONDS = 60*45          # testing (restore to 45*60 later)
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
RECOGNITION_INTERVAL = 15     # full recognition every 15 frames
# --------------------------------------

# Load face encodings
with open(ENCODINGS_FILE, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]

db.init_db()

# Runtime memory
last_message_time = {}
sent_in_email = {}
sent_out_email = {}

current_date = datetime.now().strftime("%Y-%m-%d")

# Camera setup
cap = cv2.VideoCapture(0)
cv2.namedWindow("Attendance System", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Attendance System", WINDOW_WIDTH, WINDOW_HEIGHT)

print("[INFO] Camera ON — press Q to quit")

# ROI tracking state
frame_counter = 0
tracked_faces = []  # [(loc, encoding, name)]

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (WINDOW_WIDTH, WINDOW_HEIGHT))
    now = datetime.now()

    # -------- DAILY RESET --------
    today = now.strftime("%Y-%m-%d")
    if today != current_date:
        last_message_time.clear()
        sent_in_email.clear()
        sent_out_email.clear()
        tracked_faces.clear()
        current_date = today
        print("[INFO] New day detected — attendance reset")

    frame_counter += 1

    # -------- FULL FACE RECOGNITION (PERIODIC) --------
    if frame_counter % RECOGNITION_INTERVAL == 0 or not tracked_faces:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, locations)

        tracked_faces.clear()
        for enc, loc in zip(encodings, locations):
            distances = face_recognition.face_distance(known_encodings, enc)
            best_match = np.argmin(distances)

            name = "Unknown"
            if distances[best_match] < config.TOLERANCE:
                name = known_names[best_match]

            tracked_faces.append((loc, enc, name))

    # -------- PROCESS TRACKED FACES --------
    for loc, enc, name in tracked_faces:
        top, right, bottom, left = loc
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        overlay_text = name

        if name == "Unknown":
            cv2.putText(frame, overlay_text, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            continue

        student = db.get_student_by_name(name)
        if not student:
            continue

        student_id, roll_no, parent_email = student
        open_att = db.get_open_attendance(student_id, current_date)

        # ===== CASE 1: MARK IN =====
        if not open_att and not db.has_attended_today(student_id, current_date):
            db.mark_in(student_id, current_date, now.strftime("%H:%M:%S"))

            if student_id not in sent_in_email:
                send_mark_in_email(parent_email, name, roll_no, now.strftime("%H:%M:%S"))
                sent_in_email[student_id] = True

            overlay_text = f"{roll_no} - {name} ✔ IN"
            print(f"[IN] {roll_no} - {name} at {now.strftime('%H:%M:%S')}")

        # ===== CASE 2: SESSION COMPLETED =====
        elif not open_att and db.has_attended_today(student_id, current_date):
            overlay_text = f"{roll_no} - {name} session completed"

        # ===== CASE 3: MARK OUT / BLOCK =====
        else:
            attendance_id, in_time_str = open_att
            in_time = datetime.strptime(
                f"{current_date} {in_time_str}",
                "%Y-%m-%d %H:%M:%S"
            )

            diff_seconds = (now - in_time).total_seconds()

            if diff_seconds >= MIN_OUT_SECONDS:
                db.mark_out(attendance_id, now.strftime("%H:%M:%S"))

                if student_id not in sent_out_email:
                    send_mark_out_email(parent_email, name, roll_no, now.strftime("%H:%M:%S"))
                    sent_out_email[student_id] = True

                overlay_text = f"{roll_no} - {name} ✔ OUT"
                print(f"[OUT] {roll_no} - {name} at {now.strftime('%H:%M:%S')}")

            else:
                remaining = int((MIN_OUT_SECONDS - diff_seconds) / 60)
                overlay_text = f"{roll_no} - {name} OUT blocked ({remaining} min)"

                if student_id not in last_message_time or \
                   (now - last_message_time[student_id]).total_seconds() >= config.MESSAGE_COOLDOWN:
                    print(f"[INFO] Too early for OUT: {remaining} min remaining")
                    last_message_time[student_id] = now

        cv2.putText(frame, overlay_text, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
