import os, sys, json
import hashlib
import pandas as pd

# https://newbedev.com/disable-hash-randomization-from-within-python-program
def hash(s):
    return int(hashlib.sha512(bytes(s, "utf-8")).hexdigest(), 16)

def main():
    with open("rooms.json") as f:
        rooms = json.load(f)

    # sort students by their hash
    df = pd.read_csv("canvas.csv")
    emails = df["SIS Login ID"].dropna().str.lower().tolist()
    students = [(hash(email)%10000, email) for email in emails]
    students.sort()

    # find hash cutoffs for each room
    for i, room in enumerate(rooms):
        room["cutoff"] = students[len(students) * i // len(rooms)][0]
        room["students"] = 0

    # students => rooms
    assignments = {}
    for code, email in students:
        chosen_room = None
        for room in rooms:
            if code >= room["cutoff"]:
                chosen_room = room
        chosen_room["students"] += 1
        assignments[email] = chosen_room["name"]
    print(rooms)
    with open("student_to_room.json", "w") as f:
        json.dump(assignments, f, indent=2)

    # gen messages
    emails = [{"to": email, "subject": "Final Exam Location",
               "message": f"<p>Your assignment: <b>{room}</b></p>", "html": True}
              for email, room in assignments.items()]
    with open("emails.json", "w") as f:
        json.dump(emails, f, indent=2)
        

if __name__ == '__main__':
     main()
