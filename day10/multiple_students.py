

students = [
    {"Name": "ayan", "Marks": 85},
    {"Name": "zaid", "Marks": 92},
    {"Name": "saad", "Marks": 78}
]

for student in students:
    name = student["Name"]
    marks = student["Marks"]
    print(f"Student: {name}, Marks: {marks}")