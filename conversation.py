import os, json, logging
from canvas_util import cget, cpost
from easydict import EasyDict as edict

# Import the Canvas class
from canvasapi import Canvas

logging.getLogger().setLevel(logging.INFO)

with open("graderconfig.json", "r", encoding="utf-8") as f:
    conf = edict(json.load(f))

# Canvas API URL
API_URL = f"https://canvas.wisc.edu/courses/{conf.COURSE_ID}"
# Canvas API key
API_KEY = os.environ.get("CANVAS_CRED")

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def send_notification(netid, date, score, project_id):
    students = []
    if not os.path.exists("users.json"):
        for i in range(1, 30):
            r = cget(f"users?enrollment_type=student&page={i}&per_page=100")
            if len(r) == 0:
                break
            students.extend(r)
        with open("users.json", "w") as f:
            json.dump(students, f)

    id = None
    name = None
    email = None

    with open(r"users.json", "r") as read_file:
        users = json.load(read_file)
    for user in users:
        if user["integration_id"].lower() == netid:
            id = user["id"]
            name = user["name"]
            email = user["email"]
            break

    payload = {
        "recipients": [str(id)],
        "subject": f"CS 320 - Auto Grader Gave Score {score} to Your {project_id}",
        "body": f"Hello {name}, auto grader gave score {score} to your CS 320 submission made at {date}. Please check your score here: https://tyler.caraza-harter.com/cs320/{conf.SEMESTER}/code_review.html?project_id={project_id}",
    }
    r = cpost("conversations", payload)
    logging.info(f"Received response {r} from Canvas API")
