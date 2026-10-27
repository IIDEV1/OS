# Practical Work 6 — Thread Synchronization

## Goal

Solve the producer-consumer problem with a bounded circular buffer and protect shared data from races.

## Implementation

Three producers create 1,000 items and two consumers remove them. The buffer is protected by a mutex. One semaphore tracks free slots and another tracks occupied slots. This prevents overflow, underflow and simultaneous updates of buffer indexes.

## Result

`producer_consumer.png` shows the interaction of producers and consumers. The final checks confirm that every item is consumed exactly once, no item is lost and the program terminates correctly.

## Run

```bash
python3 solution.py
```

The implementation uses the Python standard library and demonstrates the relationship between a critical section, mutex and counting semaphores.
