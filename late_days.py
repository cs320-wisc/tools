import os, json, logging
from canvas_util import cget, cpost
from canvasapi import Canvas
import os, sys
import json
from easydict import EasyDict as edict
import requests

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 send_late_days.py <pN> <score>")
        return
    
    last_project, score = sys.argv[1:]
    
    logging.getLogger().setLevel(logging.INFO)

    with open("graderconfig.json", "r", encoding="utf-8") as f:
        conf = edict(json.load(f))

    API_URL = f"https://canvas.wisc.edu/courses/{conf.COURSE_ID}"

    try:
        with open("canvas.cred") as f:
            API_KEY = f.read().strip()
    except:
        API_KEY = os.environ.get("CANVAS_CRED")

    canvas = Canvas(API_URL, API_KEY)

    students = []
    if not os.path.exists("users.json"):
        for i in range(1, 30):
            r = cget(f"users?enrollment_type=student&page={i}&per_page=100")
            if len(r) == 0:
                break
            students.extend(r)
        with open("users.json", "w") as f:
            json.dump(students, f)
        
    users_info = {}
    with open(r"users.json", "r") as read_file:
        users = json.load(read_file)

    for user in users:
        netid = user["integration_id"].lower()
        iid = user["id"]
        name = user["name"]
        email = user["email"]
        users_info[netid] = {"iid": iid, "name": name, "email": email}
    
    last_project_num = int(last_project[-1])
    for i in range(1, last_project_num + 1): 
        project = f"p{i}"
        path = os.path.join("grades", project+".json")
        with open(path) as f:
            print(path + "====================================")
            grades = json.load(f)
            print(len(grades))
            for grade in grades:
                netid = grade["net_id"]
                if netid not in users_info: 
                    print(f"Cannot find user with {netid}. Skipping canvas notification")
                else: 
                    users_info[netid][project] = grade["late_days"]
                    if i == last_project_num: 
                        users_info[netid]["remaining_late_days"] = grade["remaining_late_days"]
    
    error = []
    bodies = []
    for netid, user_info in users_info.items(): 
        # if user_info['name'] in names: 
        #     continue
        body = "PLEASE DO NOT RESPOND TO THIS MESSAGE.\n"
        body += f"Hello {user_info['name']}, underneath is a summary of late days you used up until P{last_project_num}:\n"
        for i in range(1, last_project_num + 1): 
            project = f"p{i}"
            body += f"P{i} late days used: {user_info[project]}\n"
        body += f"Remaining late days in your bank: {user_info['remaining_late_days']}"
        bodies.append(body)
        payload = {
            "recipients": [str(user_info["iid"])],
            "subject": f"CS 320 - Late Days Summary After P{last_project_num}", 
            "body": body, 
            "force_new": True
        }
        try: 
            r = cpost("conversations", payload)
            rr = logging.info(f"Received response {r} from Canvas API")
        except requests.HTTPError as exception:
            error.append(payload)
        
    with open("late_day.txt", "w") as f: 
        f.write("\n".join(bodies))
    print(payload)

main()
