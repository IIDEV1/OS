from collections import OrderedDict
PAGE=4096; tlb=OrderedDict(); K=3; hits=misses=0
refs=[0,1,2,3,0,1,4,0,2,3]
for page in refs:
    if page in tlb: hits+=1; tlb.move_to_end(page)
    else:
        misses+=1; tlb[page]=page*PAGE
        if len(tlb)>K: tlb.popitem(last=False)
    print(page,'hit' if page in tlb and page in refs[:refs.index(page)+1] else 'miss',dict(tlb))
print({'hits':hits,'misses':misses,'hit_rate':hits/(hits+misses)})
for h in (.5,.8,.9,.95): print(h,10+h*100+(1-h)*200)
