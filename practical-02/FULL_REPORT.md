# Full Report — Practical Work 2

## Purpose
This practical combines Bash scripting, Python file processing and system-call tracing.

## Implementation
`report.sh` reads test logs, filters `ERROR` or `WARN` messages, counts messages by module and prints the top results. It validates missing arguments, invalid levels, missing directories and invalid limits. `hello.py` opens a file and reports its size.

`strace` output records operations such as `open`, `read`, `write` and `close`. This connects a high-level command with the kernel operations it performs.

## Verification and result
The log-level graph, summaries and trace files are stored in `results/`. The saved output demonstrates both correct log aggregation and correct file-system interaction.
