"""NEW351 eligible-plan-byte contract; old348/349 results remain unchanged."""
def analyze(text,mode):
 r={'passed':False,'mode':mode,'intervals':[]}
 try:
  assert type(mode)==int and mode in [0,1]
  lines=[v.split() for v in text.splitlines()]
  packets=[v for v in lines if v and v[0].startswith('PRIMARY')]
  assert len(packets)==15*2*33
  times=[v for v in lines if v and v[0]=='LARGE_TIMING']
  assert len(times)==15 and [int(v[1]) for v in times]==list(range(15))
  assert all(len(v)==4 and 0<int(v[2])<=20000 and 750<=int(v[3])<=30000 for v in times)
  loops={int(v[1]):int(v[2]) for v in times};pos=0
  for id in range(15):
   pair=[]
   for phase in [0,1]:
    assert packets[pos]==['PRIMARY351_PACKET',str(id),str(phase),'1'];pos+=1;d=[]
    for index in range(32):
     v=packets[pos];pos+=1
     assert len(v)==4 and v[:3]==['PRIMARY351_AFTER' if phase else 'PRIMARY351_BEFORE',str(id),str(index)]
     n=int(v[3]);assert 0<=n<=0xffffffff;d.append(n)
    assert d[:4]==[0x50435758,351,128,mode] and d[11]==0 and not any(d[14:])
    fast=d[9]+(d[10]<<32);eligible=d[12]+(d[13]<<32)
    assert d[4]==d[6]+d[7]+d[8] and d[5]<=d[4]
    assert eligible<=d[5]*1920*1080*4
    if mode:assert d[6]+d[7]==d[5] and fast==eligible and (d[6]==0)==(fast==0)
    else:assert not any(d[6:8]+d[9:11])
    pair.append((d,fast,eligible))
   (a,fa,ea),(b,fb,eb)=pair
   assert all(b[i]>=a[i] for i in range(4,9)) and fb>=fa and eb>=ea
   delta=[b[i]-a[i] for i in range(4,9)];fast=fb-fa;eligible=eb-ea
   assert eligible<=delta[1]*1920*1080*4
   if mode:assert delta[2]+delta[3]==delta[1] and fast==eligible and (delta[2]==0)==(fast==0)
   if id%5 in [2,3]:
    assert delta[1]>=loops[id] and eligible>0
    if mode:assert delta[2]>=loops[id] and fast>0
   r['intervals'].append(dict(id=id,attempts=delta[0],eligible=delta[1],fast=delta[2],empty=delta[3],fallback=delta[4],fast_bytes=fast,eligible_plan_bytes=eligible,loops=loops[id]))
  r['passed']=True
 except (AssertionError,ValueError,KeyError,AttributeError,IndexError,TypeError) as e:r['error']=type(e).__name__
 return r
