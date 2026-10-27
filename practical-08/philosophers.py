#!/usr/bin/env python3
"""Naive deadlock and two fixes; naive mode must be externally timed out."""
import argparse
import json
import threading
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['naive','ordered','waiter'])
    parser.add_argument('--seconds',type=float,default=2)
    args=parser.parse_args()
    if args.seconds <= 0: parser.error('--seconds must be positive')
    forks=[threading.Lock() for _ in range(5)]
    seats=threading.Semaphore(4)
    start=threading.Barrier(6)
    holding_left=threading.Barrier(5)
    counts=[0]*5
    max_wait=[0.0]*5
    stats_lock=threading.Lock()
    deadline=[0.0]
    def eat(i):
        start.wait()
        while time.monotonic()<deadline[0]:
            before=time.monotonic()
            left,right=i,(i+1)%5
            if args.mode=='ordered': left,right=sorted((left,right))
            if args.mode=='waiter': seats.acquire()
            try:
                with forks[left]:
                    if args.mode=='naive': holding_left.wait()
                    with forks[right]:
                        waited=time.monotonic()-before
                        with stats_lock:
                            counts[i]+=1
                            max_wait[i]=max(max_wait[i],waited)
                        time.sleep(0.001)
            finally:
                if args.mode=='waiter': seats.release()
            time.sleep(0.001)
    threads=[threading.Thread(target=eat,args=(i,)) for i in range(5)]
    for t in threads: t.start()
    deadline[0]=time.monotonic()+args.seconds
    start.wait()
    time.sleep(args.seconds)
    with stats_lock:
        print(json.dumps({'mode':args.mode,'observation_seconds':args.seconds,'meals':counts.copy(),
                          'max_completed_wait_seconds':max_wait.copy()}),flush=True)
    # Naive deliberately stays blocked here. The supervising run script kills it.
    for t in threads: t.join()
    if args.mode!='naive':
        assert all(n>0 for n in counts)
        assert not any(f.locked() for f in forks)
        print('All threads joined; forks released',flush=True)


if __name__=='__main__': main()
