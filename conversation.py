import os, json, logging
from util import cget, cpost
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
    if not os.path.exists("users.json"):
        r = cget("users")
        with open("users.json", "w") as f:
            json.dump(r, f)

    id = None
    name = None
    email = None

    users = json.loads("users.json")
    for user in users:
        if user["integration_id"].lower() == netid:
            id = user["id"]
            name = user["name"]
            email = user["email"]
            break

    payload = {
        "recipients": [str(id)],
        "body": f"Hello {name}, auto grader gave score {score} to your CSE 320 submission made at {date}. Please check your score here: https://tyler.caraza-harter.com/cs320/{conf.SEMESTER}/code_review.html?project_id={project_id}&student_email={email}&submission_id={date}",
    }
    r = cpost("conversations", payload)
    logging.info(f"Received response {r} from Canvas API")
