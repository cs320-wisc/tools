#!/bin/sh

#Adapted from https://stackoverflow.com/questions/3258243

cd $(dirname "$0")

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

run_grader() {
    export PYTHONDONTWRITEBYTECODE=1
    export AWS_SHARED_CREDENTIALS_FILE="~/.aws/credentials"

    echo "Running Auto-grader"
    echo "\nAuto-grader for P7:"
    python3 autograder.py p7 ? -ff main.py -tc "python3 tester.py main test2" -rf results.json
    
    echo "Running Auto-grader"
    echo "\nAuto-grader for P6:"
    python3 autograder.py p6 ? -ff p6.ipynb

    echo "\nAuto-grader for P5:"
    python3 autograder.py p5 ? -ff p5.zip

    echo "\nAuto-grader for P4:"
    python3 autograder.py p4 ? -ff p4.zip -rf results.json

    echo "\nAuto-grader for P3:"
    python3 autograder.py p3 ? -ff scrape.py

    echo "\nAuto-grader for P2:"
    python3 autograder.py p2 ? -ff p2.zip

    echo "\nAuto-grader for P1:"
    python3 autograder.py p1 ? -ff p1.ipynb
}

ntpdate -s time.nist.gov
git fetch

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
    run_grader
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
    git pull
    run_grader
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi
