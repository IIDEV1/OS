# Practical Work 7 — Inter-Process Communication

## Goal

Compare the main Linux mechanisms for exchanging data and control signals between processes.

## Implemented mechanisms

- anonymous pipes;
- named FIFOs;
- Unix signals;
- the `ls | grep py` pipeline;
- Unix-domain sockets;
- shared memory;
- a calculator service using request and response FIFOs.

`pipe_demo.py` sends a message through `os.pipe()`. `pipeline.py` connects two subprocesses. `signal_demo.py` handles SIGINT and continues running until SIGTERM. The FIFO calculator validates expressions with an AST allowlist and does not use unsafe `eval`.

## Result

`ipc_comparison.png` compares transfer methods. The saved text files contain pipeline output, FIFO checks, classroom examples and benchmark results.

## Run

```bash
bash run.sh
python3 -m unittest -v test_ipc.py
python3 pipe_demo.py
python3 pipeline.py
```

Run this practical in Ubuntu/WSL2 because FIFO files, Unix sockets and `fork` are Linux features.
