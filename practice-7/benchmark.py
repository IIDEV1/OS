#!/usr/bin/env python3
"""Transfer 10^7 int64 values with shared_memory and Pipe; verify all values."""
import argparse
from array import array
import csv
import multiprocessing as mp
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
import statistics
import time


def consumer(conn, method, count):
    conn.send('ready')
    if method == 'shm':
        name = conn.recv()
        shm = SharedMemory(name=name)
        view = shm.buf.cast('q')
        try:
            assert len(view) == count
            total = sum(view)
        finally:
            view.release()
            shm.close()
    else:
        data = conn.recv_bytes()
        view = memoryview(data).cast('q')
        try:
            assert len(view) == count
            total = sum(view)
        finally:
            view.release()
    conn.send(total)
    conn.close()


def measure(method, data, count):
    context = mp.get_context('spawn')
    parent, child = context.Pipe()
    process = context.Process(target=consumer, args=(child, method, count))
    shm = None
    process.start()
    child.close()
    try:
        if not parent.poll(30) or parent.recv() != 'ready':
            raise RuntimeError('Consumer not ready')
        start = time.perf_counter()
        if method == 'shm':
            shm = SharedMemory(create=True, size=len(data)*data.itemsize)
            shm.buf[:] = memoryview(data).cast('B')
            parent.send(shm.name)  # Publication happens AFTER the complete write.
        else:
            parent.send_bytes(memoryview(data).cast('B'))
        if not parent.poll(60):
            raise TimeoutError('Consumer timed out')
        total = parent.recv()
        elapsed = time.perf_counter()-start
        assert total == count*7
        process.join(10)
        assert process.exitcode == 0
        return elapsed
    finally:
        if process.is_alive():
            process.terminate()
        process.join()
        parent.close()
        if shm is not None:
            name = shm.name
            shm.close()
            shm.unlink()
            try:
                leaked = SharedMemory(name=name)
            except FileNotFoundError:
                pass
            else:
                leaked.close()
                raise AssertionError('Shared memory still exists')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, default=10_000_000)
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    if min(args.count, args.repeats) < 1:
        parser.error('count/repeats must be positive')
    data = array('q', [7])*args.count
    assert data.itemsize == 8
    rows = []
    for repetition in range(args.repeats):
        for method in (('shm','pipe') if repetition%2 == 0 else ('pipe','shm')):
            elapsed = measure(method, data, args.count)
            rows.append({'method':method,'repeat':repetition+1,'numbers':args.count,
                         'bytes':args.count*8,'seconds':elapsed})
    out = Path('results'); out.mkdir(exist_ok=True)
    with (out/'benchmark.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    for method in ('shm','pipe'):
        print(method, 'bytes=', args.count*8, 'median_seconds=',
              round(statistics.median(r['seconds'] for r in rows if r['method']==method),6))


if __name__ == '__main__':
    main()
