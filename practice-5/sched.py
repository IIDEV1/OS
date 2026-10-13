#!/usr/bin/env python3
"""Deterministic discrete-time CPU scheduler; no third-party dependencies."""
import argparse
from collections import deque
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0


def read_processes(path):
    result = []
    with open(path, encoding='utf-8') as source:
        for line_number, line in enumerate(source, 1):
            fields = line.split('#', 1)[0].split()
            if not fields:
                continue
            if len(fields) != 4:
                raise ValueError(f'Line {line_number}: expected PID arrival burst priority')
            result.append(Process(fields[0], *map(int, fields[1:])))
    validate(result)
    return result


def validate(processes):
    if not processes:
        raise ValueError('Empty process list')
    if len({p.pid for p in processes}) != len(processes):
        raise ValueError('Duplicate PID')
    for p in processes:
        if p.pid == 'IDLE' or not p.pid or any(c.isspace() for c in p.pid):
            raise ValueError('Invalid/reserved PID')
        if any(type(v) is not int for v in (p.arrival, p.burst, p.priority)):
            raise ValueError('Times and priorities must be integers')
        if p.arrival < 0 or p.burst <= 0:
            raise ValueError('arrival >= 0, burst > 0 required')


def simulate(processes, algorithm, **params):
    """Return (start, end, PID) intervals. IDLE denotes unused CPU.

    Lower priority number is better. Equal keys prefer arrival then input order.
    RR arrivals at a slice boundary precede the requeued process.
    Aging uses cumulative READY time; time while running does not age a process.
    MLFQ preserves remaining slice on higher-level preemption; boost resets it.
    Adjacent slices of the same PID are merged (not counted as a switch).
    """
    processes = list(processes)
    validate(processes)
    algorithm = algorithm.lower()
    if algorithm not in {'fcfs', 'sjf', 'srtf', 'priority', 'rr', 'mlfq'}:
        raise ValueError('Unknown algorithm')
    quantum = params.get('quantum', 3)
    aging = params.get('aging', 0)
    quanta = tuple(params.get('quanta', (1, 2, 4)))
    boost = params.get('boost', 20)
    if type(quantum) is not int or quantum < 1:
        raise ValueError('quantum must be a positive integer')
    if type(aging) is not int or aging < 0:
        raise ValueError('aging must be a nonnegative integer')
    if len(quanta) != 3 or any(type(q) is not int or q < 1 for q in quanta) or not quanta[0] < quanta[1] < quanta[2]:
        raise ValueError('MLFQ needs three increasing positive integer quanta')
    if type(boost) is not int or boost < 1:
        raise ValueError('boost must be positive')
    pending = sorted(range(len(processes)), key=lambda i: (processes[i].arrival, i))
    remaining = [p.burst for p in processes]
    waited = [0] * len(processes)
    level = [0] * len(processes)
    budget = [quanta[0]] * len(processes)
    queues = [deque(), deque(), deque()]
    pointer = t = completed = 0
    running = None
    used = 0
    intervals = []

    def emit(pid, start, end):
        if intervals and intervals[-1][2] == pid and intervals[-1][1] == start:
            intervals[-1] = (intervals[-1][0], end, pid)
        else:
            intervals.append((start, end, pid))

    while completed < len(processes):
        # Arrivals are admitted BEFORE any expired slice is returned to a queue.
        while pointer < len(pending) and processes[pending[pointer]].arrival <= t:
            i = pending[pointer]
            queues[0].append(i)
            pointer += 1
        ready = [i for i, p in enumerate(processes) if p.arrival <= t and remaining[i] > 0]
        if not ready:
            next_time = processes[pending[pointer]].arrival
            emit('IDLE', t, next_time)
            t = next_time
            continue
        if algorithm == 'rr':
            if running is not None and used == quantum:
                queues[0].append(running)
                running = None
            if running is None:
                running = queues[0].popleft()
                used = 0
        elif algorithm == 'mlfq':
            if t > 0 and t % boost == 0:
                ordered = [i for q in queues for i in q]
                if running is not None:
                    ordered.append(running)
                queues = [deque(ordered), deque(), deque()]
                for i in ordered:
                    level[i], budget[i] = 0, quanta[0]
                running = None
            if running is not None and budget[running] == 0:
                level[running] = min(2, level[running] + 1)
                budget[running] = quanta[level[running]]
                queues[level[running]].append(running)
                running = None
            if running is not None and any(queues[k] for k in range(level[running])):
                queues[level[running]].appendleft(running)
                running = None
            if running is None:
                running = next(q.popleft() for q in queues if q)
        else:
            def key(i):
                p = processes[i]
                first = {'fcfs': p.arrival, 'sjf': p.burst, 'srtf': remaining[i],
                         'priority': p.priority - (waited[i] // aging if aging else 0)}[algorithm]
                return first, p.arrival, i
            if running is None or algorithm in {'srtf', 'priority'}:
                running = min(ready, key=key)
        emit(processes[running].pid, t, t + 1)
        for i in ready:
            if i != running:
                waited[i] += 1
        remaining[running] -= 1
        used += 1
        budget[running] -= 1
        t += 1
        if remaining[running] == 0:
            completed += 1
            running = None
    return intervals


def metrics(processes, intervals):
    validate(processes)
    lookup = {p.pid: p for p in processes}
    first, end, executed = {}, {}, {p.pid: 0 for p in processes}
    previous_end = 0
    switches = 0
    previous_pid = None
    for start, stop, pid in intervals:
        if start != previous_end or stop <= start:
            raise ValueError('Noncontiguous/invalid intervals')
        previous_end = stop
        if pid == 'IDLE':
            previous_pid = None
            continue
        if pid not in lookup or start < lookup[pid].arrival:
            raise ValueError('Execution before arrival or unknown PID')
        if previous_pid is not None and previous_pid != pid:
            switches += 1
        previous_pid = pid
        first.setdefault(pid, start)
        end[pid] = stop
        executed[pid] += stop - start
    if any(executed[p.pid] != p.burst for p in processes):
        raise ValueError('CPU service differs from burst')
    rows = []
    for p in processes:
        turn = end[p.pid] - p.arrival
        rows.append({'pid':p.pid, 'completion':end[p.pid], 'turnaround':turn,
                     'waiting':turn - p.burst, 'response':first[p.pid] - p.arrival})
    return {'per_process': rows,
            **{f'mean_{k}':sum(r[k] for r in rows)/len(rows) for k in ('waiting','turnaround','response')},
            'cpu_utilization':sum(p.burst for p in processes)/intervals[-1][1]*100,
            'switches':switches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    parser.add_argument('--algo', choices=['fcfs','sjf','srtf','priority','rr','mlfq'], default='fcfs')
    parser.add_argument('--quantum', type=int, default=3)
    parser.add_argument('--aging', type=int, default=0, help='READY ticks per priority improvement; 0 disables')
    parser.add_argument('--boost', type=int, default=20)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        processes = read_processes(args.file)
        intervals = simulate(processes, args.algo, quantum=args.quantum, aging=args.aging, boost=args.boost)
        result = metrics(processes, intervals)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps({'intervals':intervals, **result}, indent=2))
    else:
        print('Gantt:', ' | '.join(f'{a}--{b}:{p}' for a,b,p in intervals))
        print('PID   Completion Waiting Turnaround Response')
        for r in result['per_process']:
            print(f"{r['pid']:5} {r['completion']:10} {r['waiting']:7} {r['turnaround']:10} {r['response']:8}")
        for k,v in result.items():
            if k != 'per_process':
                print(f'{k}: {v:.4f}')


if __name__ == '__main__':
    main()
