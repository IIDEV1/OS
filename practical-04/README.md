# Practical Work 4 — Threads and Processes

## Goal

Compare sequential execution, multiple threads and multiple processes on the same CPU-bound calculation.

## Method

The program calculates the sum of 100,000 numbers in three modes: sequentially, with four threads and with four processes. Every mode is measured several times and the median duration is reported.

## Result

`parallel_speed.png` compares the execution time. Threads share memory and are cheap to create, but Python CPU-bound code is limited by the GIL. Processes have separate memory and higher startup overhead, but can use different CPU cores.

The result depends on the number of cores, Python version, system load and task size. For a small task, parallel startup overhead may exceed the speedup.

## Run

```bash
python3 solution.py
```
