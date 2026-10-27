#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python3 -m unittest -v test_sched.py
python3 report.py
python3 sched.py --algo rr --quantum 3 set1.txt
