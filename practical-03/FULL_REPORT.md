# Full Report — Practical Work 3

## Purpose
This practical explains Linux process creation, process hierarchy and process lifetime.

## Implementation
`ptree.py` reads `/proc/<PID>/status` and builds a process tree. Other programs demonstrate `fork`, `exec`, `wait`, zombie processes, orphan processes and Copy-on-Write memory behavior.

A zombie has finished but remains in the process table until the parent calls `wait`. An orphan continues after its parent exits and is adopted by init/systemd. Copy-on-Write delays copying memory pages until a process changes them.

## Verification and result
`process_states.png` and the saved text outputs document the observed PIDs, parent PIDs and states. The work verifies that process life-cycle behavior is controlled by the kernel.
