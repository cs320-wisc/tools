import logging, os, json, requests
from easydict import EasyDict as edict

logging.getLogger().setLevel(logging.INFO)

with open("graderconfig.json", "r", encoding="utf-8") as f:
    conf = edict(json.load(f))

try:
    with open("canvas.cred") as f:
        cred = f.read().strip()
except:
    cred = os.environ.get("CANVAS_CRED")


def cget(url):
    url = f"https://canvas.wisc.edu/api/v1/courses/{conf.COURSE_ID}/{url}"
    logging.info(f"GET, url: {url}")
    r = requests.get(url, headers={"Authorization": "Bearer " + cred})
    r.raise_for_status()
    return r.json()


def cpost(url, payload):
    url = f"https://canvas.wisc.edu/api/v1/{url}"
    logging.info(f"POST, url: {url}")
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + cred}
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()


def cput(url, data):
    url = f"https://canvas.wisc.edu/api/v1/courses/{conf.COURSE_ID}/{url}"
    logging.info(f"PUT, url: {url}")
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + cred}
    r = requests.put(url, headers=headers, data=json.dumps(data))
    r.raise_for_status()
    return r.json()
