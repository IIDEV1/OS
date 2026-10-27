# Operating Systems Practical Works

This repository contains eight Variant B practical works for the Operating Systems course. Each practical includes source programs, a detailed English report, saved execution results, tests, logs, and a visualization where appropriate.

## Contents

| Work | Topic | Folder |
|---|---|---|
| 1 | Linux users, groups, permissions and diagnostics | [practical-01](practical-01/) |
| 2 | Bash and system calls | [practical-02](practical-02/) |
| 3 | Linux processes | [practical-03](practical-03/) |
| 4 | Threads and processes | [practical-04](practical-04/) |
| 5 | CPU scheduling simulator | [practical-05](practical-05/) |
| 6 | Thread synchronization | [practical-06](practical-06/) |
| 7 | Inter-process communication | [practical-07](practical-07/) |
| 8 | Deadlocks and the Banker algorithm | [practical-08](practical-08/) |

## Repository structure

Every practical folder contains the implementation, a `README.md` report, and a `results/` directory. The results directory stores logs, tables, test output, and graphs so that the work can be reviewed without running every command again.

## Environment

The experiments target Linux or Ubuntu/WSL2. Python 3.10+, Bash and standard Linux utilities are required. Some tasks use Linux-specific facilities such as `/proc`, `fork`, `fcntl`, FIFO files, Unix sockets, signals and Linux scheduling APIs.

## Main topics

The project covers permissions, shell scripting, system calls, process creation, process states, threads, CPU scheduling, synchronization, IPC and deadlock prevention.

## Results

The complete list of graphs and saved outputs is available in [RESULTS.md](RESULTS.md). Each practical README explains the experiment, the meaning of the output and the final conclusion.
