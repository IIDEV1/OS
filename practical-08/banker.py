#!/usr/bin/env python3
"""Banker's safety algorithm and transactional requests, JSON input."""
import argparse
from copy import deepcopy
import json

# Точный учебный пример со слайда (Веха 8.3, часть 1).
AVAILABLE = [3, 3, 2]
ALLOCATION = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
MAX = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]


def is_safe(available, allocation, maximum):
    """Return (safe, order), following the classroom slide line by line."""
    n, m = len(allocation), len(available)
    need = [[maximum[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False] * n
    order = []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                for j in range(m):
                    work[j] += allocation[i][j]
                finish[i] = True
                order.append(f"P{i}")
                progress = True
    return all(finish), order


class Banker:
    def __init__(self, available, allocation, maximum):
        self.available = list(available)
        self.allocation = deepcopy(allocation)
        self.maximum = deepcopy(maximum)
        n, m = len(allocation), len(available)
        if not n or not m or len(maximum) != n:
            raise ValueError('Empty/inconsistent matrices')
        for row in [available, *allocation, *maximum]:
            if len(row) != m or any(type(v) is not int or v < 0 for v in row):
                raise ValueError('Nonnegative integer vectors of equal width required')
        if any(a > b for ar, mr in zip(allocation,maximum) for a,b in zip(ar,mr)):
            raise ValueError('Allocation exceeds Max')

    @property
    def need(self):
        return [[m-a for m,a in zip(mr,ar)] for mr,ar in zip(self.maximum,self.allocation)]

    def safety(self):
        work = self.available.copy()
        pending = set(range(len(self.allocation)))
        sequence = []
        while pending:
            progress = False
            for pid in sorted(pending):
                if all(n <= w for n,w in zip(self.need[pid],work)):
                    work = [w+a for w,a in zip(work,self.allocation[pid])]
                    pending.remove(pid)
                    sequence.append(pid)
                    progress = True
            if not progress:
                return False, sequence
        return True, sequence

    def valid_sequence(self, sequence):
        if sorted(sequence) != list(range(len(self.allocation))):
            return False
        work = self.available.copy()
        for pid in sequence:
            if any(n > w for n,w in zip(self.need[pid],work)):
                return False
            work = [w+a for w,a in zip(work,self.allocation[pid])]
        return True

    def request(self, pid, vector):
        if type(pid) is not int or not 0 <= pid < len(self.allocation):
            raise ValueError('Unknown PID')
        if len(vector) != len(self.available) or any(type(v) is not int or v < 0 for v in vector):
            raise ValueError('Invalid request vector')
        if any(r > n for r,n in zip(vector,self.need[pid])):
            return False, 'Request exceeds Need'
        if any(r > a for r,a in zip(vector,self.available)):
            return False, 'Not enough Available; wait'
        old_available, old_allocation = self.available.copy(), self.allocation[pid].copy()
        self.available = [a-r for a,r in zip(self.available,vector)]
        self.allocation[pid] = [a+r for a,r in zip(self.allocation[pid],vector)]
        safe, sequence = self.safety()
        if not safe:
            self.available, self.allocation[pid] = old_available, old_allocation
            return False, 'Unsafe; rolled back'
        return True, 'Safe sequence: '+' '.join(f'P{i}' for i in sequence)


def load(path):
    with open(path) as stream:
        data = json.load(stream)
    return Banker(data['available'], data['allocation'], data['maximum'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    parser.add_argument('--requests', action='store_true', help='Read lines: P1 1 0 2')
    args = parser.parse_args()
    bank = load(args.file)
    print('Need:', bank.need)
    safe, sequence = bank.safety()
    print('SAFE '+ ' '.join(f'P{i}' for i in sequence) if safe else 'UNSAFE')
    if args.requests:
        import sys
        for line in sys.stdin:
            if not line.strip(): continue
            try:
                pid, *vector = line.split()
                accepted, reason = bank.request(int(pid.removeprefix('P')), list(map(int, vector)))
                print('GRANTED' if accepted else 'DENIED', reason, 'Available=',bank.available)
            except ValueError as error:
                print('ERROR', error)


if __name__ == '__main__': main()
