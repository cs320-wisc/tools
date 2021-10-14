import os, sys, json, copy, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict as ddict

with open("graderconfig.json") as f:
    CONF = json.load(f)

COURSE = "b"
not_reviewed = {}
CR_URL = f'https://tyler.caraza-harter.com/cs320/{CONF["SEMESTER"]}/code_review.html?project_id=%s&student_email=%s@wisc.edu'

# https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib
def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def try_read_json(path, default={}):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return copy.deepcopy(default)

class Grades:
    def __init__(self, project):
        self.project = project

        if not os.path.exists("snapshot"):
            raise Exception(f"need to run 'python3 s3interface.py -dp --prefix \"{COURSE}\"' first")

        with open(f"snapshot/{COURSE}/config.json") as f:
            deadlines = json.load(f)["deadlines"]
        # end of day (add 24 hours)
        self.deadline = datetime.strptime(deadlines[project], "%m/%d/%y").astimezone(tz=timezone.utc) + timedelta(days=1)

        with open(f"snapshot/{COURSE}/roster.json") as f:
            net_ids = {row['net_id'] for row in json.load(f) if row['enrolled']}

        self.extensions = self.get_extensions()
        self.grade_rows = [self.get_student_grade(nid) for nid in net_ids]

    # returns dict
    # key: submission file path
    # val: days extended
    def get_extensions(self):
        extensions = ddict(int)

        dirname = 'snapshot/%s/extensions/%s/' % (COURSE, self.project)
        if not os.path.exists(dirname):
            return extensions
        for name in os.listdir(dirname):
            if not name.endswith(".json"):
                continue
            path = os.path.join(dirname, name)
            with open(path) as f:
                days = json.load(f)["days"]
            net_id = name.split("*at*")[0]
            links = self.get_proj_links(net_id)
            for link in links:
                with open(link) as f:
                    sub = json.load(f)['symlink']
                    extensions[sub] = max(extensions[sub], days)
        return extensions

    def dump(self, path):
        with open(path, "w") as f:
            f.write('[\n')
            for i, row in enumerate(self.grade_rows):
                json.dump(row, f)
                if i < len(self.grade_rows) - 1:
                    f.write(",")
                f.write("\n")
            f.write(']\n')


    def get_proj_links(self, net_id):
        dirname = 'snapshot/%s/projects/%s/%s*at*wisc.edu' % (COURSE, self.project, net_id)
        link = None
        if os.path.exists(dirname):
            return [os.path.join(dirname, p) for p in os.listdir(dirname) if p.endswith('-link.json')]
        return []


    def get_student_grade(self, net_id):
        bonus_days = 0

        grade = None
        links = sorted(self.get_proj_links(net_id))
        for i, link in enumerate(links):
            with open(link) as f:
                submission_dir = json.load(f)['symlink']
            grade2 = self.get_submission_grade(net_id, submission_dir)
            grade2["latest_submission"] = (i == len(links) - 1)
            # only take a later submission over a prior one if the
            # score is better, because the earlier one will incur
            # fewer late days
            if grade == None or grade2["score"] > grade["score"]:
                grade = grade2

            # if they submit on time and get 50%, they get 3 extra days
            if grade2["test_score"] >= 50 and grade2["late_days"] <= 0:
                bonus_days = 3

        else:
            submission_dir = None

        if grade == None:
            grade = self.get_submission_grade(net_id, None)
        grade["bonus_days"] = bonus_days

        return grade


    def get_submission_grade(self, net_id, submission_dir):
        # we need to check four files:
        # - tests
        # - CR
        # - submission (to determine lateness)
        # - extensions (to adjust lateness)

        late_days = 0
        submitted = ""
        test_score = 0

        ready = False
        if submission_dir:
            sub = try_read_json(os.path.join("snapshot", COURSE, submission_dir, "submission.json"), {})
            test = try_read_json(os.path.join("snapshot", COURSE, submission_dir, "test.json"), {})
            test_score = test.get("score", 0)
            cr = try_read_json(os.path.join("snapshot", COURSE, submission_dir, "cr.json"), {})

            if sub != {}:
                submitted = datetime.strptime(sub["submit_time_utc"], "%Y-%m-%d %H:%M:%S")
                submitted = utc_to_local(submitted)
                late_days = math.ceil((submitted - self.deadline) / timedelta(days=1))
                late_days -= self.extensions[submission_dir]
                late_days = max(late_days, 0)
                submitted = datetime.strftime(submitted, "%Y-%m-%d %H:%M:%S")

            if sub != {} and test != {} and (cr != {} or self.project in not_reviewed):
                test_score = test.get("score", 0)
                ta_deduction = cr.get("points_deducted", 0)
                comment_count = 0
                for comments in cr.get("highlights", {}).values():
                    comment_count += len(comments)
                ready = True

        if not ready:
            ta_deduction = 0
            comment_count = 0
            score = 0
        else:
            score = max(test_score - ta_deduction, 0)
        cr_url = CR_URL % (self.project, net_id)

        return {"project": self.project, "net_id": net_id, "test_score": test_score,
                "ta_deduction": ta_deduction, "score": score, "submitted": submitted, "late_days": late_days,
                "comment_count": comment_count, "ready": ready, "code_review_url": cr_url}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_grades.py p1 [p2 ...]")
    if not os.path.exists("grades"):
        os.mkdir("grades")
    for project in sys.argv[1:]:
        Grades(project).dump(os.path.join('grades', project+'.json'))


if __name__ == '__main__':
     main()
