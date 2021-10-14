import os, sys
import json
import pandas as pd

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 grades_to_canvas.py <canvas.csv> <pN>")
        return

    cfile, proj = sys.argv[1:]
    c = pd.read_csv(cfile)
    orig_cols = list(c.columns)
    c = c.set_index("SIS Login ID")
    col = [name for name in c.columns if name.split()[0].upper() == proj.upper()]
    assert len(col) == 1
    col = col[0]
    best_score = c[col].iat[0]

    with open(os.path.join("grades", proj+".json")) as f:
        grades = json.load(f)
    for grade in grades:
        email = (grade["net_id"]+"@wisc.edu").upper()
        if not email in c.index:
            print("Dropped?", email.lower())
            continue
        if grade["late_days"] > grade["bonus_days"]:
            print(f"Too late ({grade['score']}):", email.lower())
            score = 0
        else:
            score = grade["score"]
        c.at[email, col] = score / 100 * best_score

    c = c.reset_index()[orig_cols]
    print("saving new canvas file at canvas-new.csv")
    c.to_csv("canvas-new.csv", index=False)

main()
