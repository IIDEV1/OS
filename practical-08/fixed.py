#!/usr/bin/env python3
import threading


def main():
    locks = [threading.Lock(),threading.Lock()]
    start = threading.Barrier(2)
    counts = [0,0]
    def worker(i):
        start.wait()
        for _ in range(1000):
            with locks[0], locks[1]:
                counts[i] += 1
    threads = [threading.Thread(target=worker,args=(i,)) for i in range(2)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=10)
    assert not any(t.is_alive() for t in threads)
    assert counts == [1000,1000]
    print('Ordered locks:', counts)


if __name__ == '__main__': main()
