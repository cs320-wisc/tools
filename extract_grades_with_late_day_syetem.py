import os, sys, json, copy, math, pytz
from datetime import datetime, timezone, timedelta
from collections import defaultdict as ddict

with open("graderconfig.json") as f:
    CONF = json.load(f)

COURSE = "a"
not_reviewed = {"p7"}
CR_URL = f"https://www.msyamkumar.com/cs320/{CONF['SEMESTER']}/code_review.html?project_id=%s&student_email=%s@wisc.edu"

BANK = 12
PENALTY = 0.05

def utc_to_cst(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('US/Central'))

def try_read_json(path, default={}):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return copy.deepcopy(default)

def get_deadlines(): 
    with open(f"snapshot/{COURSE}/config.json") as f:
        config = json.load(f)
        deadlines_txt = config["deadlines"]
        soft_days = config["soft_days"]
        hard_days = config["hard_days"]
        soft_days["p3"], hard_days["p3"] = 3, 5
    deadlines = {}
    for p, ddl in deadlines_txt.items(): 
        deadline = datetime.strptime(ddl, "%m/%d/%y")
        deadline = pytz.timezone('America/Chicago').localize(deadline)
        deadline = deadline + timedelta(days=1)
        deadlines[p] = deadline
    return deadlines, soft_days, hard_days

def get_extensions(project):
    extensions = {}

    extensions_dir = f"snapshot/{COURSE}/extensions/{project}/"
    if not os.path.exists(extensions_dir):
        return extensions
    for name in os.listdir(extensions_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(extensions_dir, name)
        with open(path) as f:
            extension_days = json.load(f)["days"]
        net_id = name.split("*at*")[0]
        if net_id in extensions: 
            extensions[net_id] = max(extension_days, extensions[net_id])
        else: 
            extensions[net_id] = extension_days
    return extensions

def dump(project, grades):
    with open(os.path.join('grades', project+'.json'), "w") as f:
        f.write('[\n')
        for i, row in enumerate(grades):
            json.dump(row, f)
            if i < len(grades) - 1:
                f.write(",")
            f.write("\n")
        f.write(']\n')
    
def get_grade(project, net_id, latest_sub_dir, submit_time, sub_late_days, extension, sub_soft_days, remaining_late_days, late_penalty): 
    if latest_sub_dir is None: 
        return {"project": project, "net_id": net_id, 
            "test_score": 0, 
            "submit_time": None, "late_days": 0, "late_penalty": 0, "remaining_late_days": remaining_late_days, 
            "ta_deduction": 0, "score": 0,
            "comment_count": 0, "ready": False, "code_review_url": None}
    sub = try_read_json(os.path.join("snapshot", COURSE, latest_sub_dir, "submission.json"), {})
    test = try_read_json(os.path.join("snapshot", COURSE, latest_sub_dir, "test.json"), {})
    cr = try_read_json(os.path.join("snapshot", COURSE, latest_sub_dir, "cr.json"), {})
    
    ready = False
    test_score = 0
        
    if sub and test: 
        test_score = test.get("score", 0)
    
    default_general_comments = ["Great job!  Please check comments below.", 
                                "Good job, please check comments below.", 
                                "Please check comments below."]
    
    changed_general_comments = False
    reviewer_email = None
    if sub and test and (cr or project in not_reviewed):
        ta_deduction = cr.get("points_deducted", 0)
        reviewer_email = cr.get("reviewer_email", 0)
        general_comments = cr.get("general_comments", "")
        
        if general_comments not in default_general_comments: 
            changed_general_comments = True
        comment_count = 0
        for comments in cr.get("highlights", {}).values():
            comment_count += len(comments)
        ready = True
         
    if not ready:
        ta_deduction = 0
        comment_count = 0
        score = 0
        
    else:
        score = max(test_score - ta_deduction, 0) * (1 - late_penalty)
    
    cr_url = CR_URL % (project, net_id)
    
    res = {"project": project, "net_id": net_id, 
            "test_score": test_score, 
            "submit_time": submit_time, "extension": extension, 
            "late_days": sub_late_days, "late_penalty": late_penalty, "remaining_late_days": remaining_late_days, 
            "ta_deduction": ta_deduction, "score": score,
            "comment_count": comment_count, "ready": ready, "code_review_url": cr_url,
            "reviewer_email": reviewer_email, "changed_general_comments": changed_general_comments, "comment_count": comment_count
          } 
    return res
    
    
def extract_grades(projects): 
    with open(f"snapshot/{COURSE}/roster.json") as f:
        net_ids = {row['net_id'] for row in json.load(f) if row['enrolled']}
        
    deadlines, soft_days, hard_days = get_deadlines()

    remaining_late_days = ddict(lambda: BANK)
    last_proj_num = int(projects[-1][-1]) 
    
    for i in range(1, last_proj_num + 1): 
        project = f"p{i}"
        
        extensions = get_extensions(project)
        
        grades = []
        
        for nid in net_ids: 
            
            individual_dir = f"snapshot/{COURSE}/projects/{project}/{nid}*at*wisc.edu"
            links = []
            if os.path.exists(individual_dir):
                links = [os.path.join(individual_dir, p) for p in os.listdir(individual_dir) if p.endswith('-link.json')]
            
            if not links:  
                if project in projects: 
                    grades.append(get_grade(project, nid, None, None, 0, 0, soft_days[project], remaining_late_days[nid], None))          
                continue
            
            links = sorted(links, reverse=True)

            latest_sub_dir = None
            links_idx = 0
            flag = False 
            while True and links_idx < len(links): 
                with open(links[links_idx]) as f:
                    submission_dir = json.load(f)['symlink']
                sub = try_read_json(os.path.join("snapshot", COURSE, submission_dir, "submission.json"), {})
                
                if sub: 
                    submitted = datetime.strptime(sub["submit_time_utc"], "%Y-%m-%d %H:%M:%S")
                    submitted = utc_to_cst(submitted)
                    submit_time = datetime.strftime(submitted, "%Y-%m-%d %H:%M:%S %z")
                    sub_late_days = math.ceil((submitted - deadlines[project]) / timedelta(days=1))
                    extension = 0 
                    if nid in extensions: 
                        extension = extensions[nid]
                    sub_late_days -= extension
                    if project == "p3": 
                        sub_late_days -= 9
                    sub_late_days = max(sub_late_days, 0)
                        
                        
                    if sub_late_days <= hard_days[project]: 
                        latest_sub_dir = submission_dir
                        use_late_days = max(min(remaining_late_days[nid], sub_late_days, soft_days[project]), 0)
                        rem_late_days = remaining_late_days[nid] - use_late_days
                        unaccounted_late_days = sub_late_days - use_late_days
                        late_penalty = unaccounted_late_days * PENALTY
                        remaining_late_days[nid] = rem_late_days
                        
                        flag = True
                        break
                        
                        
                links_idx += 1
                
                if not flag and len(links) > 0: 
                    print(nid)
            
            if project in projects: 
                grades.append(get_grade(project, nid, latest_sub_dir, submit_time, use_late_days, extension, soft_days[project], remaining_late_days[nid], late_penalty)) 
        
        if project in projects: 
            dump(project, grades)
            
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_grades.py p1 [p2 ...]")
    if not os.path.exists("snapshot"):
        raise Exception(f"need to run 'python3 s3interface.py -dp --prefix \"{COURSE}\"' first")
    if not os.path.exists("grades"):
        os.mkdir("grades")
    extract_grades(sorted(sys.argv[1:]))
    
    
if __name__ == '__main__':
    main()