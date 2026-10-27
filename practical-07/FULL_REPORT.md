# Full Report — Practical Work 7

## Purpose
This practical compares Linux mechanisms for communication and control between processes.

## Implementation
The work includes anonymous pipes, named FIFOs, signals, a subprocess pipeline, Unix-domain sockets, shared memory and a calculator using request and response FIFOs. The calculator validates expressions through an AST allowlist and does not use unsafe `eval`.

## Verification and result
`ipc_comparison.png` and the benchmark files compare the measured communication methods. Pipe, FIFO, signal, pipeline and socket outputs are saved in `results/` so each experiment can be checked independently.
