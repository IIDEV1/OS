#!/usr/bin/env python3
"""Generate reproducible datasets, metrics and an SVG chart using stdlib."""
import csv
import json
import random
from pathlib import Path
from sched import Process, read_processes, simulate, metrics

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'


def write_data(name, ps):
    (ROOT/name).write_text('# Generated dataset; seed=42. PID arrival burst priority\n'+
                          ''.join(f'{p.pid} {p.arrival} {p.burst} {p.priority}\n' for p in ps),encoding='utf-8')


def main():
    OUT.mkdir(exist_ok=True)
    rng=random.Random(42)
    write_data('set2.txt',[Process(f'P{i+1}',rng.randrange(0,16),rng.randrange(12,41),rng.randrange(0,6)) for i in range(20)])
    write_data('set3.txt',[Process('LONG',0,80,5)]+[Process(f'S{i}',i*2,1+i%3,0) for i in range(1,20)])
    write_data('aging.txt',[Process('LOW',0,6,10)]+[Process(f'H{i}',i,1,0) for i in range(100)])
    rows=[]
    schedules={}
    for dataset in ('set1','set2','set3'):
        ps=read_processes(ROOT/f'{dataset}.txt')
        for algo in ('fcfs','sjf','srtf','rr','priority','mlfq'):
            intervals=simulate(ps,algo)
            m=metrics(ps,intervals)
            schedules[f'{dataset}/{algo}']={'intervals':intervals,**m}
            rows.append({'dataset':dataset,'algorithm':algo,**{k:v for k,v in m.items() if k!='per_process'}})
    with (OUT/'comparison.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (OUT/'schedules.json').write_text(json.dumps(schedules,indent=2),encoding='utf-8')
    sweep=[]
    ps=read_processes(ROOT/'set2.txt')
    for q in range(1,11):
        m=metrics(ps,simulate(ps,'rr',quantum=q))
        sweep.append({'quantum':q,'mean_waiting':m['mean_waiting'],'switches':m['switches']})
    with (OUT/'rr_quantum.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(sweep[0]));writer.writeheader();writer.writerows(sweep)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420" viewBox="0 0 960 420">',
         '<rect width="960" height="420" fill="white"/>',
         '<g font-family="sans-serif" font-size="13" fill="#14243a">',
         '<text x="30" y="27" font-size="20">Round Robin: quantum trade-off (set2)</text>']
    for panel,(key,title,color) in enumerate([('mean_waiting','Mean waiting (ticks)','#186cbe'),('switches','Process switches','#bd5124')]):
        x0=65+panel*470; y0=340; top=max(r[key] for r in sweep)*1.1
        svg.append(f'<text x="{x0}" y="65" font-size="16">{title}</text>')
        for j in range(6):
            y=y0-j*48
            svg.append(f'<path d="M{x0},{y}h370" stroke="#dde3eb"/><text x="{x0-8}" y="{y+4}" text-anchor="end">{top*j/5:.0f}</text>')
        points=[]
        for r in sweep:
            x=x0+(r['quantum']-1)*40; y=y0-r[key]/top*240
            points.append(f'{x},{y:.2f}')
            svg.append(f'<circle cx="{x}" cy="{y:.2f}" r="4" fill="{color}"/><text x="{x}" y="365" text-anchor="middle">{r["quantum"]}</text>')
        svg.append(f'<polyline points="{" ".join(points)}" stroke="{color}" stroke-width="2" fill="none"/>')
        svg.append(f'<text x="{x0+145}" y="395">Quantum (ticks)</text>')
    svg.append('</g></svg>')
    (OUT/'rr_quantum.svg').write_text('\n'.join(svg),encoding='utf-8')
    ps=read_processes(ROOT/'aging.txt')
    aging={str(a):metrics(ps,simulate(ps,'priority',aging=a)) for a in (0,2)}
    (OUT/'aging.json').write_text(json.dumps(aging,indent=2),encoding='utf-8')
    lines=['| Набор | Алгоритм | Ожидание | Оборот | Отклик | CPU, % | Переключения |',
           '|---|---|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['dataset']} | {r['algorithm']} | {r['mean_waiting']:.2f} | {r['mean_turnaround']:.2f} | {r['mean_response']:.2f} | {r['cpu_utilization']:.2f} | {r['switches']} |")
    (OUT/'table.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('\n'.join(lines))
    print('LOW, no aging:',aging['0']['per_process'][0])
    print('LOW, aging=2:',aging['2']['per_process'][0])


if __name__=='__main__': main()
