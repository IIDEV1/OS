# Practical Work 3 — Linux Processes

## Goal

Study process creation, the process tree and the main process states provided by Linux.

## Implemented tasks

- read process information directly from `/proc`;
- build a process tree in `ptree.py`;
- create child processes with `fork()`;
- replace a process image with `exec()`;
- demonstrate `wait`, zombie and orphan processes;
- demonstrate Copy-on-Write memory behavior.

## Result

`process_states.png` compares the observed process states. A zombie has already finished but remains in the process table until its parent calls `wait`. An orphan continues after its original parent exits and is adopted by init/systemd. Copy-on-Write delays memory copying until a process changes a shared page.

## Run

```bash
python3 ptree.py
python3 runner.py
python3 zombie.py
python3 orphan.py
python3 cow.py
```
