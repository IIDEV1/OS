from pathlib import Path
import hashlib,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
seen={}; duplicates=[]
for p in root.rglob('*'):
 if p.is_file() and p.name!='dedup.py':
  h=hashlib.sha256(p.read_bytes()).hexdigest()
  if h in seen: duplicates.append((p,seen[h]))
  else: seen[h]=p
for p,first in duplicates: print(f'{p} == {first}')
print('duplicates:',len(duplicates))
