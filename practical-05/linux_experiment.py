#!/usr/bin/env python3
"""Bounded Linux experiments: nice weights and optionally a short SCHED_FIFO window."""
import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time


def worker(cpu, nice):
    os.sched_setaffinity(0,{cpu})
    os.nice(nice)
    # Hard cap on uninterrupted real-time execution, independent of the parent.
    resource.setrlimit(resource.RLIMIT_RTTIME,(600000,700000))
    resource.setrlimit(resource.RLIMIT_CPU,(10,11))
    print('READY',flush=True)
    start,duration=map(float,sys.stdin.readline().split())
    time.sleep(max(0,start-time.monotonic()))
    end=start+duration
    number=1
    while time.monotonic()<end:
        for _ in range(2000): number=(number*1664525+1013904223)&0xffffffff


def cpu_ns(pid):
    return int(Path(f'/proc/{pid}/schedstat').read_text().split()[0])


def trial(nices,duration,fifo=False):
    cpus=sorted(os.sched_getaffinity(0))
    if len(cpus)<2:
        raise RuntimeError('Need >=2 CPUs: parent watchdog must run outside worker CPU')
    cpu=cpus[-1]
    os.sched_setaffinity(0,set(cpus[:-1]))
    children=[]
    try:
        for nice in nices:
            child=subprocess.Popen([sys.executable,__file__,'--worker',str(cpu),str(nice)],
                                   stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
            children.append(child)
            if child.stdout.readline().strip()!='READY': raise RuntimeError('Worker failed')
        start=time.monotonic()+0.3
        for child in children:
            child.stdin.write(f'{start} {duration}\n');child.stdin.flush()
        time.sleep(max(0,start+0.5-time.monotonic()))
        begin=[cpu_ns(c.pid) for c in children]
        policy_change=None
        if fifo:
            result=subprocess.run(['chrt','-f','-p','10',str(children[0].pid)],capture_output=True,text=True)
            if result.returncode:
                raise RuntimeError('SCHED_FIFO unavailable: '+result.stderr.strip())
            policy_change=subprocess.check_output(['chrt','-p',str(children[0].pid)],text=True)
            time.sleep(0.35)
        else:
            time.sleep(duration-1.0)
        finish=[cpu_ns(c.pid) for c in children]
        if fifo:
            subprocess.run(['chrt','-o','-p','0',str(children[0].pid)],check=True,capture_output=True)
        elapsed=[(b-a)/1e9 for a,b in zip(begin,finish)]
        total=sum(elapsed)
        return {'cpu':cpu,'nice':nices,'cpu_seconds':elapsed,'shares':[x/total for x in elapsed],
                'policy':policy_change,'window_seconds':0.35 if fifo else duration-1.0}
    finally:
        for child in children:
            if child.poll() is None: child.terminate()
        for child in children:
            try: child.wait(timeout=2)
            except subprocess.TimeoutExpired: child.kill();child.wait()
        os.sched_setaffinity(0,set(cpus))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker',nargs=2,type=int)
    parser.add_argument('--fifo',action='store_true',help='Requires CAP_SYS_NICE/root; bounded 0.35 s window')
    args=parser.parse_args()
    if args.worker:
        worker(*args.worker);return
    root=Path(__file__).resolve().parent/'results'
    root.mkdir(exist_ok=True)
    result={'kernel':os.uname().release,'python':sys.version,'measurement':'/proc/PID/schedstat field 1 delta',
            'weights':[1024,335,110,36], 'expected_shares':[w/1505 for w in [1024,335,110,36]],
            'trials':[trial([0,5,10,15],4) for _ in range(3)]}
    if args.fifo:
        try: result['fifo']=trial([0,0,0,0],2,fifo=True)
        except (OSError,RuntimeError,subprocess.SubprocessError) as error:
            result['fifo_error']=str(error)
    path=root/('linux_fifo.json' if args.fifo else 'linux_nice.json')
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
