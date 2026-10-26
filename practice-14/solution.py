from pathlib import Path
from time import perf_counter
p=Path('io_test.bin'); size=10*1024*1024
for label,chunk in [('1-byte',b'x'),('64-KB',b'x'*65536)]:
 t=perf_counter()
 with p.open('wb',buffering=0) as f:
  for _ in range(size//len(chunk)): f.write(chunk)
 print(label,perf_counter()-t)
p.unlink()
