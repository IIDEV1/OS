#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mkdir -p results
{ uname -sr; python3 --version; } > results/environment.txt
python3 -m unittest -v test_ipc.py 2>&1 | tee results/tests.txt
python3 pipe_demo.py | tee results/pipe.txt
python3 pipeline_demo.py | tee results/pipeline.txt
timeout 180s python3 benchmark.py | tee results/benchmark.txt
