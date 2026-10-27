# Full Report — Practical Work 4

## Purpose
This practical compares sequential execution, threads and processes for the same CPU-bound calculation.

## Method
The program calculates the sum of 100,000 numbers sequentially, with four threads and with four processes. Each mode is measured repeatedly and the median time is used.

Threads share memory and have lower creation overhead, but Python CPU-bound work is limited by the GIL. Processes have separate memory and more startup overhead, but can use multiple CPU cores.

## Verification and result
`parallel_speed.png` compares the measured durations. The result depends on task size, CPU cores, Python version and system load; therefore the practical demonstrates measurement rather than claiming one universal winner.
