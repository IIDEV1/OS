#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p results
{ uname -sr; python3 --version; } > results/environment.txt
python3 -m unittest -v test_deadlocks.py 2>&1 | tee results/tests.txt
python3 banker.py bank1.txt | tee results/bank1.txt
python3 banker.py bank2.txt | tee results/bank2.txt
printf 'P1 1 0 2\n' | python3 banker.py bank1.txt --requests | tee results/request.txt
python3 detector.py events.txt | tee results/detector.txt
python3 fixed.py | tee results/fixed.txt
python3 tracked_demo.py | tee results/tracked.txt
set +e
timeout 3s python3 deadlock.py > results/deadlock.txt 2>&1
status=$?
set -e
if [[ "$status" != 124 ]]; then echo "Expected deadlock timeout, got $status"; exit 1; fi
set +e
timeout 4s python3 philosophers.py naive --seconds 2 > results/philosophers-naive.txt 2>&1
status=$?
set -e
if [[ "$status" != 124 ]]; then echo "Expected philosopher timeout, got $status"; exit 1; fi
timeout 10s python3 philosophers.py ordered --seconds 2 | tee results/philosophers-ordered.txt
timeout 10s python3 philosophers.py waiter --seconds 2 | tee results/philosophers-waiter.txt
echo 'Expected hangs terminated; corrected programs finished.'
