import random
import unittest
from sched import Process as P, simulate, metrics, read_processes


class SchedulingTests(unittest.TestCase):
    def test_reference(self):
        ps = read_processes('set1.txt')
        # Handout FCFS values contain an arithmetic error; see README calculation.
        for algo, wait, turn in [('fcfs',8.75,15.25), ('srtf',6.5,13.0), ('rr',13.5,20.0)]:
            m = metrics(ps, simulate(ps,algo,quantum=3))
            self.assertEqual((m['mean_waiting'],m['mean_turnaround']), (wait,turn))

    def test_rr_arrival_at_boundary(self):
        self.assertEqual(simulate([P('a',0,4),P('b',2,1)],'rr',quantum=2),
                         [(0,2,'a'),(2,3,'b'),(3,5,'a')])

    def test_srtf_preempts(self):
        self.assertEqual(simulate([P('a',0,6),P('b',2,1)],'srtf'),
                         [(0,2,'a'),(2,3,'b'),(3,7,'a')])

    def test_idle_and_metrics(self):
        ps = [P('a',2,2),P('b',7,1)]
        for algo in ('fcfs','sjf','srtf','priority','rr','mlfq'):
            ints = simulate(ps,algo)
            self.assertEqual(ints,[(0,2,'IDLE'),(2,4,'a'),(4,7,'IDLE'),(7,8,'b')])
            m=metrics(ps,ints)
            self.assertEqual(m['mean_waiting'],0)
            self.assertEqual(m['cpu_utilization'],37.5)

    def test_priority_and_aging(self):
        ps = [P('low',0,2,8)] + [P(f'h{i}',i,1,0) for i in range(60)]
        without=metrics(ps,simulate(ps,'priority'))['per_process'][0]['response']
        with_aging=metrics(ps,simulate(ps,'priority',aging=2))['per_process'][0]['response']
        self.assertEqual(without,60)
        self.assertLess(with_aging,without)

    def test_mlfq_preserves_slice(self):
        self.assertEqual(simulate([P('a',0,8),P('b',0,8),P('c',3,1)],'mlfq',boost=100),
                         [(0,1,'a'),(1,2,'b'),(2,3,'a'),(3,4,'c'),(4,5,'a'),
                          (5,7,'b'),(7,11,'a'),(11,15,'b'),(15,16,'a'),(16,17,'b')])

    def test_mlfq_boost_changes_service(self):
        ps=[P('a',0,20),P('b',0,20)]
        self.assertNotEqual(simulate(ps,'mlfq',boost=5),simulate(ps,'mlfq',boost=100))

    def test_random_invariants(self):
        rng=random.Random(42)
        for _ in range(50):
            ps=[P(str(i),rng.randrange(10),rng.randrange(1,12),rng.randrange(5)) for i in range(8)]
            for algo in ('fcfs','sjf','srtf','priority','rr','mlfq'):
                m=metrics(ps,simulate(ps,algo,aging=3,boost=7))
                for r,p in zip(m['per_process'],ps):
                    self.assertGreaterEqual(r['waiting'],0)
                    self.assertGreaterEqual(r['response'],0)
                    self.assertEqual(r['turnaround']-r['waiting'],p.burst)
                    self.assertLessEqual(r['response'],r['waiting'])
            self.assertEqual(simulate(ps,'rr',quantum=1000),simulate(ps,'fcfs'))

    def test_invalid_input(self):
        for ps in ([],[P('a',0,0)],[P('a',-1,3)],[P('a',0,1),P('a',2,1)]):
            with self.assertRaises(ValueError): simulate(ps,'rr')
        with self.assertRaises(ValueError): simulate([P('a',0,1)],'rr',quantum=0)


if __name__=='__main__': unittest.main(verbosity=2)
