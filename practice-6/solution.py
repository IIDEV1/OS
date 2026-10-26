from threading import Thread, Semaphore, Lock, Condition
from collections import deque
N=1000; CAP=5; q=deque(); empty=Semaphore(CAP); full=Semaphore(0); lock=Lock(); produced=[]; consumed=[]
def producer(start,count):
    for x in range(start,start+count):
        empty.acquire()
        with lock: q.append(x); produced.append(x)
        full.release()
def consumer():
    while True:
        full.acquire()
        with lock:
            if q: x=q.popleft()
            else: x=None
        empty.release()
        if x is None: return
        consumed.append(x)
threads=[Thread(target=producer,args=(i*N//3,(i+1)*N//3-i*N//3)) for i in range(3)]
threads += [Thread(target=consumer) for _ in range(2)]
for t in threads[:3]: t.start()
for t in threads[3:]: t.start()
for t in threads[:3]: t.join()
for _ in threads[3:]:
    empty.acquire(); q.append(None); full.release()
for t in threads[3:]: t.join()
assert sorted(produced)==sorted(consumed)==list(range(N))
print('OK: 3 producer, 2 consumer, capacity=5, items=1000')
