# Full Report — Practical Work 6

## Purpose
This practical solves the producer-consumer problem with a bounded circular buffer.

## Implementation
Three producers generate 1,000 items and two consumers remove them. A mutex protects the buffer and two counting semaphores track free and occupied slots. This prevents races, overflow and underflow.

## Verification and result
The final checks confirm exactly-once consumption, no lost items and successful termination. `producer_consumer.png` records the interaction between producers and consumers and the saved output documents the final counters.
