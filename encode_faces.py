import face_recognition
import os
import pickle

DATASET_DIR = "dataset"
ENCODINGS_DIR = "encodings"
ENCODINGS_FILE = os.path.join(ENCODINGS_DIR, "face_encodings.pkl")

os.makedirs(ENCODINGS_DIR, exist_ok=True)

known_encodings = []
known_names = []

print("[INFO] Encoding faces...")

for person in os.listdir(DATASET_DIR):
    person_path = os.path.join(DATASET_DIR, person)
    if not os.path.isdir(person_path):
        continue

    for img in os.listdir(person_path):
        img_path = os.path.join(person_path, img)

        image = face_recognition.load_image_file(img_path)
        encs = face_recognition.face_encodings(image)

        if len(encs) == 0:
            print(f"[SKIPPED] No face in {img_path}")
            continue

        known_encodings.append(encs[0])
        known_names.append(person)

with open(ENCODINGS_FILE, "wb") as f:
    pickle.dump({"encodings": known_encodings, "names": known_names}, f)

print("[SUCCESS] Face encodings saved.")
