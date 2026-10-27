# Practical Work 8 — Deadlocks and the Banker Algorithm

## Goal

Reproduce a real deadlock, fix it by imposing a lock order, detect cyclic waiting and implement the Banker safety algorithm.

## Implemented tasks

- create two threads that hold A and B in opposite order;
- capture the blocked stacks with `faulthandler`;
- fix the program by acquiring locks in the same order;
- implement safe-state checks and resource requests in the Banker algorithm;
- detect cycles in a wait-for log;
- compare naive, ordered and waiter solutions for dining philosophers;
- use tracked locks to record ownership and waiting.

## Banker result

`Need = Max - Allocation`. A state is safe when at least one completion order exists for all processes. The program tests both a safe matrix and an unsafe matrix and rolls back a request if it would make the state unsafe.

## Result

`deadlock_states.png` shows normal execution, cyclic waiting, the detected deadlock and the fixed version. The saved files include the deadlock trace, fixed output, banker sequences and philosopher experiments.

## Run

```bash
bash run.sh
timeout 3s python3 deadlock.py
python3 fixed.py
python3 banker.py bank1.txt
```

The intentionally deadlocking example is expected to time out. The corrected programs must finish successfully.
