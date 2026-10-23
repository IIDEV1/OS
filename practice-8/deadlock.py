#!/usr/bin/env python3
"""Classroom example: two threads intentionally deadlock."""
import faulthandler
import threading
import time

faulthandler.dump_traceback_later(5, exit=True)

lock_a = threading.Lock()
lock_b = threading.Lock()


def worker1():
    with lock_a:
        print("T1 взял A, жду B", flush=True)
        time.sleep(0.1)
        with lock_b:
            print("T1 взял A и B", flush=True)


def worker2():
    with lock_b:
        print("T2 взял B, жду A", flush=True)
        time.sleep(0.1)
        with lock_a:
            print("T2 взял B и A", flush=True)


def main():
    t1 = threading.Thread(target=worker1)
    t2 = threading.Thread(target=worker2)
    t1.start(); t2.start()
    t1.join(); t2.join()
    faulthandler.cancel_dump_traceback_later()
    print("Готово")


if __name__ == '__main__': main()
