#!/usr/bin/env python3
"""Intentionally hangs. Inspect faulthandler output; stop with timeout 3s."""
import faulthandler
import threading


def main():
    a, b = threading.Lock(), threading.Lock()
    barrier = threading.Barrier(2)
    def worker(first, second):
        with first:
            barrier.wait()
            with second:
                print('unreachable',flush=True)
    faulthandler.dump_traceback_later(1)
    threads = [threading.Thread(target=worker,args=(a,b)),threading.Thread(target=worker,args=(b,a))]
    for thread in threads: thread.start()
    print('Both threads take their first lock, then wait for the second',flush=True)
    for thread in threads: thread.join()


if __name__ == '__main__': main()
