"""Nonrecursive Lock wrapper with atomic wait-for-graph accounting."""
import threading
from detector import WaitGraph, find_cycle


class DeadlockError(RuntimeError):
    pass


class Registry:
    def __init__(self):
        self.condition = threading.Condition()
        self.state = WaitGraph()


class TrackedLock:
    def __init__(self, registry, name):
        self.registry, self.name = registry, name
        self.lock = threading.Lock()

    def acquire(self):
        tid = threading.get_ident()
        r = self.registry
        # Actual ownership and graph updates use the SAME metadata mutex.
        with r.condition:
            r.state.waiting[tid] = self
            try:
                cycle = find_cycle(r.state.graph())
                if cycle:
                    raise DeadlockError('Wait-for cycle: '+' -> '.join(map(str,cycle)))
                while self in r.state.owners:
                    r.condition.wait()
                    cycle = find_cycle(r.state.graph())
                    if cycle:
                        raise DeadlockError('Wait-for cycle: '+' -> '.join(map(str,cycle)))
                assert self.lock.acquire(blocking=False)
                r.state.owners[self] = tid
            finally:
                r.state.waiting.pop(tid,None)
        return True

    def release(self):
        r = self.registry
        with r.condition:
            if r.state.owners.get(self) != threading.get_ident():
                raise RuntimeError('Release by non-owner')
            self.lock.release()
            del r.state.owners[self]
            r.condition.notify_all()

    def __enter__(self):
        self.acquire(); return self

    def __exit__(self,*args):
        self.release()
