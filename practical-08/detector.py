#!/usr/bin/env python3
"""Wait-for graph for single-instance, nonrecursive resources."""
import argparse
import json


def find_cycle(graph):
    visited, active, path = set(), set(), []
    def visit(node):
        if node in active:
            return path[path.index(node):] + [node]
        if node in visited:
            return None
        active.add(node); path.append(node)
        for target in sorted(graph.get(node, set())):
            cycle = visit(target)
            if cycle:
                return cycle
        path.pop(); active.remove(node); visited.add(node)
        return None
    for node in sorted(graph):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


class WaitGraph:
    def __init__(self):
        self.owners = {}
        self.waiting = {}

    def graph(self):
        result = {}
        for thread, resource in self.waiting.items():
            owner = self.owners.get(resource)
            if owner is not None:
                result.setdefault(thread,set()).add(owner)
        return result

    def event(self, kind, thread, resource):
        if kind == 'acquire':
            if resource in self.owners:
                raise ValueError('Resource already owned')
            if thread in self.waiting and self.waiting[thread] != resource:
                raise ValueError('Thread waits on another resource')
            self.owners[resource] = thread
            self.waiting.pop(thread,None)
        elif kind == 'release':
            if self.owners.get(resource) != thread:
                raise ValueError('Release by non-owner')
            del self.owners[resource]
        elif kind == 'wait':
            if thread in self.waiting:
                raise ValueError('Thread already waiting')
            self.waiting[thread] = resource
        else:
            raise ValueError('Expected acquire/release/wait')
        return find_cycle(self.graph())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file')
    args = parser.parse_args()
    graph = WaitGraph()
    with open(args.file) as stream:
        for number,line in enumerate(stream,1):
            fields = line.split('#',1)[0].split()
            if not fields: continue
            cycle = graph.event(*fields)
            print(number, json.dumps({k:sorted(v) for k,v in graph.graph().items()}),
                  'CYCLE: '+' -> '.join(cycle) if cycle else 'NO CYCLE')


if __name__ == '__main__': main()
