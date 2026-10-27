# Practical Work 5 — CPU Scheduling Simulator

## Goal

Implement and compare common CPU scheduling algorithms and calculate waiting, turnaround and response metrics.

## Implemented algorithms

- FCFS;
- non-preemptive SJF;
- preemptive SRTF;
- Priority scheduling with aging;
- Round Robin;
- MLFQ.

The simulator also measures CPU utilization, context switches and the effect of the Round Robin quantum. A Linux experiment demonstrates `nice` and `SCHED_FIFO` when the environment allows it.

## Input and metrics

Each process is described by `PID arrival burst priority`. Waiting time is the time spent in the ready queue. Turnaround time is completion minus arrival. Response time is the time from arrival to the first CPU allocation.

The saved tables and `scheduling_metrics.png` compare the algorithms. The README and `results/` files also document the reproducibility of the input sets and the arithmetic check for the FCFS example.

## Run

```bash
bash run.sh
python3 sched.py --algo rr --quantum 3 set1.txt
python3 sched.py --algo srtf set1.txt
```
