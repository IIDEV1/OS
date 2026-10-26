def schedule(req,head,algo,disk=200):
 r=req[:]; out=[]; cur=head
 if algo=='FCFS': order=r
 elif algo=='SSTF':
  order=[]
  while r: x=min(r,key=lambda z:abs(z-cur)); order.append(x); r.remove(x); cur=x
 else:
  left=sorted([x for x in r if x<cur]); right=sorted([x for x in r if x>=cur]); order=(right+([disk-1] if algo=='SCAN' else [])+left[::-1])
 cur=head; total=0
 for x in order: total+=abs(x-cur); cur=x
 return order,total
req=[98,183,37,122,14,124,65,67]
for a in ('FCFS','SSTF','SCAN'): print(a,schedule(req,53,a))
