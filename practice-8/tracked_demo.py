#!/usr/bin/env python3
import threading
from tracked_lock import Registry, TrackedLock, DeadlockError


def main():
    registry = Registry()
    a,b = TrackedLock(registry,'A'),TrackedLock(registry,'B')
    barrier = threading.Barrier(2)
    errors, completed = [], []
    def worker(i, first, second):
        try:
            with first:
                barrier.wait()
                with second:
                    completed.append(i)
        except DeadlockError as error:
            errors.append(str(error))
    threads = [threading.Thread(target=worker,args=(0,a,b)),threading.Thread(target=worker,args=(1,b,a))]
    for t in threads: t.start()
    for t in threads: t.join(timeout=5)
    assert not any(t.is_alive() for t in threads)
    assert len(errors)==1 and len(completed)==1
    assert not registry.state.owners and not registry.state.waiting
    print('Cycle prevented:',errors[0]); print('Completed:',completed,'Graph empty: True')


if __name__ == '__main__': main()
