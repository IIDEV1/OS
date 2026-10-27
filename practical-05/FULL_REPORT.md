# Full Report — Practical Work 5

## Purpose
This practical implements a CPU scheduler simulator and compares the effect of scheduling policies on process performance.

## Algorithms
The simulator includes FCFS, SJF, SRTF, Priority with aging, Round Robin and MLFQ. It calculates waiting time, turnaround time, response time, CPU utilization and context switches.

The experiments also vary the Round Robin quantum and demonstrate how aging prevents starvation. When supported by Linux, `nice` and `SCHED_FIFO` are measured separately.

## Verification and result
The results directory contains exact schedules, CSV/JSON tables, tests and `scheduling_metrics.png`. The metrics make it possible to explain why a policy that improves response time can increase context switches or average waiting time.
