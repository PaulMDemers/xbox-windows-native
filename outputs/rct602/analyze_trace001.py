"""Summarize actual matched calls; never reinterpret requests as invocations."""
from collections import Counter
from trace_oracle601 import parse
NAMES={1:'LoadLibraryA',2:'GetProcAddress',3:'BitBlt',4:'CreateDIBSection',5:'DirectDrawCreate',
 6:'IDirectDraw.Release',7:'IDirectDraw.SetCooperativeLevel',8:'IDirectDraw.CreateSurface',
 9:'IDirectDrawSurface.Release',10:'IDirectDrawSurface.GetSurfaceDesc',11:'StretchDIBits',
 12:'unused',13:'IDirectDrawSurface.Blt',14:'original_probe'}
def analyze(text,base,size):
 r=parse(text);calls=r['calls'];main={i:c for i,c in calls.items() if base<=c['ret']<base+size}
 pending=None;resolutions=[]
 for line in text.splitlines():
  p=line.split()
  if p[0] in ['PROC','LOAD','ORD']:pending=p
  if p[0]=='CALL':
   i=int(p[1],16);c=calls[i]
   if c['api'] in [1,2]:
    assert pending and int(pending[1],16)==c['tid'] and int(pending[2],16)==c['ret']
    if c['api']==2 and i in main:
     name='#'+str(int(pending[4],16)) if pending[0]=='ORD' else bytes.fromhex(pending[4]).decode('ascii')
     resolutions.append(dict(name=name,module=c['a'],result=c['result']))
   pending=None
 graphics=[]
 for i,c in main.items():
  if c['api']<3:continue
  assert c['api']!=14
  row=dict(id=i,name=NAMES[c['api']],args=r['args'][i],result=c['result'])
  if i in r['outputs']:row['output_pointer']=r['outputs'][i]
  if i in r['objects']:row['object']=r['objects'][i]
  graphics.append(row)
 return dict(passed=True,total_pairs=len(calls),main_pairs=len(main),other_pairs=len(calls)-len(main),
  all_call_counts=dict(Counter(NAMES[c['api']] for c in calls.values())),
  main_call_counts=dict(Counter(NAMES[c['api']] for c in main.values())),
  sampled_limits=[dict(api=NAMES[a],recorded=n,address=p) for a,n,p in r['caps']],
  selected_resolutions=[v for v in resolutions if v['name'] in ['BitBlt','CreateDIBSection','StretchDIBits','DirectDrawCreate']],
  main_graphics_calls=graphics,modules=r['modules'],
  limits='Actual paired invocations within this bounded instrumented PC run. Per-API32-call caps; other APIs/interfaces and later capped calls are unobserved. No pristine game control, timing or GPU claim.')
