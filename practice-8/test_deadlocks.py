from copy import deepcopy
import subprocess
import sys
import unittest
from banker import load
from detector import WaitGraph, find_cycle
from tracked_lock import Registry, TrackedLock, DeadlockError


class DeadlockTests(unittest.TestCase):
    def test_reference_states_and_sequence(self):
        bank=load('bank1.txt')
        self.assertTrue(bank.safety()[0])
        self.assertTrue(bank.valid_sequence([1,3,4,2,0]))
        self.assertTrue(bank.valid_sequence(bank.safety()[1]))
        self.assertFalse(load('bank2.txt').safety()[0])

    def test_grant_reference_request(self):
        bank=load('bank1.txt')
        self.assertTrue(bank.request(1,[1,0,2])[0])
        self.assertEqual(bank.available,[2,3,0])
        self.assertEqual(bank.allocation[1],[3,0,2])
        self.assertTrue(bank.safety()[0])

    def test_unsafe_rollback(self):
        bank=load('bank1.txt')
        old=deepcopy(bank.__dict__)
        granted,reason=bank.request(4,[3,3,0])
        self.assertFalse(granted)
        self.assertIn('rolled back',reason)
        self.assertEqual(bank.__dict__,old)

    def test_invalid_and_unavailable(self):
        bank=load('bank1.txt');old=deepcopy(bank.__dict__)
        for pid,vector in [(1,[-1,0,0]),(99,[0,0,0]),(1,[0])]:
            with self.assertRaises(ValueError):bank.request(pid,vector)
        self.assertFalse(bank.request(1,[2,0,0])[0]) # Above need.
        self.assertFalse(bank.request(0,[4,0,0])[0]) # Available insufficient.
        self.assertEqual(bank.__dict__,old)

    def test_wait_graph_cycle_and_release(self):
        graph=WaitGraph()
        for event in [('acquire','T1','A'),('acquire','T2','B'),('wait','T1','B')]:
            self.assertIsNone(graph.event(*event))
        self.assertEqual(graph.event('wait','T2','A'),['T1','T2','T1'])
        self.assertIsNone(graph.event('release','T1','A'))
        self.assertIsNone(graph.event('acquire','T2','A'))
        with self.assertRaises(ValueError):graph.event('release','T1','B')
        self.assertIsNone(find_cycle({'A':{'B'},'B':{'C'}}))

    def test_tracked_recursive_acquire(self):
        registry=Registry();lock=TrackedLock(registry,'A')
        with lock:
            with self.assertRaises(DeadlockError):lock.acquire()
        self.assertFalse(registry.state.owners)
        self.assertFalse(registry.state.waiting)

    def test_tracked_and_ordered_terminate(self):
        for script in ('fixed.py','tracked_demo.py'):
            for _ in range(3):
                result=subprocess.run([sys.executable,script],capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':unittest.main(verbosity=2)
