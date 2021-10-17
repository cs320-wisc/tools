import json
import sys
import numpy as np


def main(project):
    ta_assignments = json.load(open(f"{project}-cr-assignments.json"))
    grades = json.load(open(f"grades/{project}.json"))
    stats = {}
    for grade in grades:
        ta = ta_assignments[f"{grade['net_id']}@wisc.edu"]
        new_stats = {}
        if ta in stats:
            current_stats = stats[ta]
            new_stats = {
                "deductions": current_stats["deductions"] + [grade["ta_deduction"]],
                "test_scores": current_stats["test_scores"] + [grade["test_score"]],
                "scores": current_stats["scores"] + [grade["score"]],
            }
        else:
            new_stats = {
                "deductions": [grade["ta_deduction"]],
                "test_scores": [grade["test_score"]],
                "scores": [grade["score"]],
            }
        stats[ta] = new_stats

    results = []

    for ta in stats:
        deductions = stats[ta]["deductions"]

        log = (
            f"TA {ta}: \t "
            f"mean deduction {np.mean(deductions)}, "
            f"median deduction {np.median(deductions)}, "
            f"max deduction {np.max(deductions)}, "
            f"number of students affected by deductions {np.count_nonzero(deductions)}/{len(deductions)}, "
            f"mean score before and after deduction {np.mean(stats[ta]['test_scores'])} -> {round(np.mean(stats[ta]['test_scores']) - np.mean(deductions), 2)}"
        )

        results.append((np.mean(deductions), log))

    results.sort(key=lambda tup: tup[0])

    for result in results:
        print(result[1])


if __name__ == "__main__":
    project = sys.argv[1]
    main(project)
