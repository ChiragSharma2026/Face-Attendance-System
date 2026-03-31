import db

db.init_db()

students = [
    ("CS101", "Chirag", "xyz@gmail.com"),
    ("CS102", "Aditya", "abc@gmail.com")
]

for roll, name, email in students:
    db.add_student(roll, name, email)

print("Students registered successfully.")
