import os, json, logging, yaml
from util import cget, cpost

# Import the Canvas class
from canvasapi import Canvas

logging.getLogger().setLevel(logging.INFO)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Canvas API URL
API_URL = f"https://canvas.wisc.edu/courses/{config['course_id']}"
# Canvas API key
API_KEY = os.environ.get("CANVAS_CRED")

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def send_notification(netid, date, score):
    if not os.path.exists("users.json"):
        r = cget("users")
        with open("users.json", "w") as f:
            json.dump(r, f)

    id = None
    name = None

    users = json.loads("users.json")
    for user in users:
        if user["integration_id"].lower() == netid:
            id = user["id"]
            name = user["name"]
            break

    payload = {
        "recipients": [str(id)],
        "body": f"Hello {name}, auto grader gave score {score} to your CSE 320 submission made at {date}.",
    }
    r = cpost("conversations", payload)
    logging.info(f"Received response {r} from Canvas API")
