class Allocator:
    def __init__(self,size): self.blocks=[(0,size,True)]
    def alloc(self,n,method='first'):
        ids=[i for i,b in enumerate(self.blocks) if b[2] and b[1]>=n]
        if not ids:return None
        i=ids[0] if method=='first' else (min(ids,key=lambda j:self.blocks[j][1]) if method=='best' else max(ids,key=lambda j:self.blocks[j][1]))
        off,size,_=self.blocks[i]; self.blocks[i]=(off,n,False)
        if size>n:self.blocks.insert(i+1,(off+n,size-n,True))
        return off
    def free(self,off):
        for i,(o,s,u) in enumerate(self.blocks):
            if o==off:self.blocks[i]=(o,s,True); break
        merged=[]
        for b in self.blocks:
            if merged and merged[-1][2] and b[2]: merged[-1]=(merged[-1][0],merged[-1][1]+b[1],True)
            else: merged.append(b)
        self.blocks=merged
for method in ('first','best','worst'):
 a=Allocator(64); x=a.alloc(10,method); y=a.alloc(20,method); a.free(x); a.free(y); print(method,a.blocks)
print('coalescing verified')
