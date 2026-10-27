# Full Report — Practical Work 8

## Purpose
This practical studies deadlocks, their detection, prevention and safe resource allocation.

## Implementation
Two threads intentionally acquire locks in opposite order to reproduce a deadlock. The fixed version uses one global lock order. The Banker implementation calculates `Need = Max - Allocation`, tests safe sequences and rolls back unsafe resource requests.

The practical also includes a wait-for graph detector, tracked locks and three dining-philosopher strategies.

## Verification and result
`deadlock_states.png` and the saved traces show the blocked state, the corrected execution, safe and unsafe Banker matrices, and philosopher results. The intentionally blocked example is expected to time out; corrected programs must finish successfully.
