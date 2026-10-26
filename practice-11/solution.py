def fifo(refs,k):
 from collections import deque
 q=deque(); s=set(); f=0
 for x in refs:
  if x not in s:
   f+=1
   if len(q)==k:s.remove(q.popleft())
   q.append(x); s.add(x)
 return f
def lru(refs,k):
 q=[]; f=0
 for x in refs:
  if x in q:q.remove(x)
  else:
   f+=1
   if len(q)==k:q.pop(0)
  q.append(x)
 return f
refs=[1,2,3,1,4,2,5,1,2,3,4,5]
for k in range(1,9): print(k,fifo(refs,k),lru(refs,k))
