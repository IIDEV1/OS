# Practical Work 2 — Bash and System Calls

## Goal

Process log files with Bash and connect shell commands with the system calls performed by the operating system.

## Implemented tasks

- generate a collection of test log files;
- implement `report.sh` with `ERROR`, `WARN` and `--top N` arguments;
- count messages by module and sort the result;
- validate missing arguments, invalid levels and invalid directories;
- implement `hello.py` to report a file size;
- record file access with `strace`.

## Result

`log_levels.png` compares the number of messages produced by modules or log levels. The trace files show calls such as `open`, `read`, `write` and `close` made by the programs.

## Run

```bash
./report.sh data ERROR --top 3
python3 hello.py data/01.log
```

The scripts require Linux/Bash because the task uses shell pipelines and system-call tracing.
