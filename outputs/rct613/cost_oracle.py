"""Independent, fail-closed raw counter interpreter. No guest/host clock mixing."""
def decode(text):
 """Strict format: tag id index qpc tick kernel user working peak pagefile."""
 rows=[];freq=None
 tags={'START','END','OBSERVER_START','OBSERVER_END','SAMPLE','ALLOC_BEFORE','READY','WORK_START','WORK_END'}
 for line in text.splitlines():
  t=line.split();assert t
  if t[0]=='FREQ':
   assert freq is None and not rows and len(t)==2
   freq=int(t[1],16);assert 0<freq<2**63
  elif t[0] in tags:
   assert freq and len(t)==10
   v=[int(x,16 if i in [2,4,5] else 10) for i,x in enumerate(t[1:])]
   assert all(x>=0 for x in v) and 0<=v[3]<2**32
   rows.append((t[0],v))
  else:
   assert t[0] in {'CASE','RESULT','PASS','CONTROL_PASS','RESTART'}
   rows.append((t[0],[int(x) for x in t[1:]]))
 assert freq
 return freq,rows

def span(a,b,f):
 assert a[0]==b[0] and b[2]>=a[2] and b[4]>=a[4] and b[5]>=a[5]
 q=(b[2]-a[2])/f;tick=((b[3]-a[3])&0xffffffff)/1000
 cpu=(b[4]+b[5]-a[4]-a[5])/1e7
 assert q>0 and abs(q-tick)<=max(.1,q*.05),'clock disagreement'
 assert cpu<=q+.1,'CPU exceeds one logical CPU'
 return dict(qpc_seconds=q,tick_seconds=tick,cpu_seconds=cpu,user_seconds=(b[5]-a[5])/1e7,kernel_seconds=(b[4]-a[4])/1e7)

def validate(parent,children):
 f,rows=decode(parent)
 assert rows[-2:]==[('CONTROL_PASS',[]),('RESTART',[])]
 assert len(children)==6
 assert all(v and 0<=v[0]<6 for tag,v in rows[:-2])
 result=[]
 for i in range(6):
  cf,cr=decode(children[i]);assert cf==f and cr[-1]==('PASS',[])
  assert len(cr)==6
  child={}
  for tag,v in cr[:4]:
   assert tag not in child and v[0]==i and v[1]==0
   child[tag]=v
  assert set(child)=={'ALLOC_BEFORE','READY','WORK_START','WORK_END'}
  assert [tag for tag,_ in cr[:4]]==['ALLOC_BEFORE','READY','WORK_START','WORK_END']
  assert cr[4][0]=='RESULT' and len(cr[4][1])==3
  cid,iterations,checksum=cr[4][1];assert cid==i
  # Repeated affine transform modulo 2^32 by exponentiation, not the worker loop.
  n=33554432 if i>=2 else 0;mul,add=1,0;a,c=1664525,1013904223;power=n
  while power:
   if power&1:mul,add=(a*mul)&0xffffffff,(a*add+c)&0xffffffff
   a,c=(a*a)&0xffffffff,(a*c+c)&0xffffffff;power>>=1
  assert iterations==n and checksum==(mul+add)&0xffffffff
  assert child['READY'][8]-child['ALLOC_BEFORE'][8]>=8*1024**2,'committed memory growth'
  assert child['READY'][6]-child['ALLOC_BEFORE'][6]>=4*1024**2,'resident memory growth'
  selected=[(tag,v) for tag,v in rows[:-2] if v and v[0]==i]
  fixed={}
  samples=[]
  for tag,v in selected:
   if tag=='SAMPLE':samples.append(v)
   else:assert tag not in fixed;fixed[tag]=v
  assert set(fixed)=={'START','END','OBSERVER_START','OBSERVER_END','CASE'}
  assert fixed['CASE']==[i,int(i in [1,3,4]),len(samples),0,0]
  assert bool(samples)==(i in [1,3,4])
  assert all(s[0]==i and s[1]==j for j,s in enumerate(samples))
  seq=[fixed['START'],*samples,fixed['END']]
  for a,b in zip(seq,seq[1:]):
   assert b[2]>=a[2] and b[4]>=a[4] and b[5]>=a[5]
  for tag in ['READY','WORK_START','WORK_END']:
   assert child[tag][2]<=fixed['END'][2]
  assert fixed['START'][2]<=child['WORK_START'][2]<=child['WORK_END'][2]
  assert fixed['START'][4]<=child['WORK_START'][4]<=child['WORK_END'][4]<=fixed['END'][4]
  assert fixed['START'][5]<=child['WORK_START'][5]<=child['WORK_END'][5]<=fixed['END'][5]
  work=span(child['WORK_START'],child['WORK_END'],f)
  observed=span(fixed['START'],fixed['END'],f)
  observer=span(fixed['OBSERVER_START'],fixed['OBSERVER_END'],f)
  if i<2:
   assert 1.9<=work['qpc_seconds']<=5 and work['cpu_seconds']<work['qpc_seconds']*.25
  else:assert work['cpu_seconds']>=.1
  result.append(dict(case=i,periodic=bool(samples),samples=len(samples),work=work,observed=observed,observer=observer))
 assert len([r for r in rows if r[0]=='CASE'])==6
 return dict(passed=True,frequency=f,cases=result,scope='Original guest process counters under PC TCG; not game FPS, host CPU utilization or Xbox performance.')
