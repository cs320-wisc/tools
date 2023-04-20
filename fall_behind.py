import os, sys
import json
import pandas as pd

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 fall_behind.py <pN>")
        return

    canvas_file, project = "canvas.csv", sys.argv[1]
    canvas = pd.read_csv(canvas_file)
    all_canvas = set(canvas["SIS Login ID"])
    canvas = canvas.set_index("SIS Login ID")
    
    dropped = []
    no_submission = []
    submission_test_score_0 = []
    submission_test_score_pos = []
    all_sub = []
    late = {}
    tas = {}
    remaining_late_days = []
    with open(os.path.join("grades", project+".json")) as f:
        grades = json.load(f)
    for grade in grades:
        email = (grade["net_id"]+"@wisc.edu").lower()
        email_upper = email.upper()
        if email_upper not in canvas.index:
            dropped.append(email)
        else:
            if grade["submit_time"] is None: 
                no_submission.append(email)
            else: 
                all_sub.append(email)
                if grade["test_score"] == 0: 
                    submission_test_score_0.append(email)
                else: 
                    submission_test_score_pos.append(email)
                if grade["late_days"] > 0: 
                    late[email] = [grade["late_days"], grade["submit_time"]]
                remaining_late_days.append((grade["remaining_late_days"], email))
                if grade["reviewer_email"] is not None:
                    reviewer = grade["reviewer_email"]
                    if reviewer not in tas: 
                        tas[reviewer] = {"points_deducted": [], "general_comment_changed_count": 0, "comment_count": 0}
                    tas[reviewer]["points_deducted"].append(grade["ta_deduction"])
                    if grade["changed_general_comments"]: 
                        tas[reviewer]["general_comment_changed_count"] += 1
                    tas[reviewer]["comment_count"] += grade["comment_count"]
                    
    print(f"Dropped list: ({len(dropped)})")
    for e in dropped: 
        print(e)
    print("=========================================")
    print(f"No submission list: ({len(no_submission)})")
    for e in no_submission: 
        print(e)
    print("=========================================")
    print(f"Submission but test score 0 list: ({len(submission_test_score_0)})")
    for e in submission_test_score_0: 
        print(e)
    print("=========================================")
    print(f"Submission but test score positive list: ({len(submission_test_score_pos)})")
    print("=========================================")
    print("late list:")
    for e, i in late.items(): 
        print(f"{e}\t\t{i[0]} {i[1]}")
    print("=========================================")
    with open("website.txt") as f: 
        website = f.read()
    website = set([x.split()[0] for x in website.split("\n")])
    print(website.difference(set(all_sub)))
    print(set(all_sub).difference(website))
    print("=========================================")
    for ta, info in tas.items(): 
        sub_count = len(info["points_deducted"])
        print(f"{ta} \t avg points deducted: {round(sum(info['points_deducted']) / sub_count, 3)} \t avg comments left: {round(info['comment_count'] / sub_count, 3)} \t avg general comment changed: {round(info['general_comment_changed_count'] / sub_count, 3)}") 
    # print("=========================================")
    # for i in sorted(remaining_late_days, reverse=True): 
    #     print(i)
main()