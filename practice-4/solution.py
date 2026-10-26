from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import perf_counter
from statistics import median
from pathlib import Path

def chunk_sum(xs): return sum(xs)
def timed(fn):
    t=perf_counter(); value=fn(); return value, perf_counter()-t

def main():
    numbers=list(range(1,100001)); Path("numbers.txt").write_text("\n".join(map(str,numbers)))
    parts=[numbers[i::4] for i in range(4)]
    runs=[]
    for label,fn in [
      ("one-thread",lambda:sum(numbers)),
      ("4-threads",lambda:sum(ThreadPoolExecutor(4).map(chunk_sum,parts))),
      ("4-processes",lambda:sum(ProcessPoolExecutor(4).map(chunk_sum,parts))),
    ]:
        vals=[timed(fn) for _ in range(3)]; assert all(v[0]==sum(numbers) for v in vals)
        runs.append((label,median(v[1] for v in vals)))
    for label,t in runs: print(f"{label}: {t:.6f}s")

if __name__ == "__main__": main()
