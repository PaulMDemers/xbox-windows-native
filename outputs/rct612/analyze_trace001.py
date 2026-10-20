"""Independent parsed invocations/header/phase summary; no assumed game format."""
from collections import Counter
from trace_oracle import parse
NAMES={1:'LoadLibraryA',2:'GetProcAddress',3:'BitBlt',4:'CreateDIBSection',5:'DirectDrawCreate',6:'IDirectDraw.Release',7:'IDirectDraw.SetCooperativeLevel',8:'IDirectDraw.CreateSurface',9:'IDirectDrawSurface.Release',10:'IDirectDrawSurface.GetSurfaceDesc',11:'StretchDIBits',12:'unused',13:'IDirectDrawSurface.Blt',14:'original_probe',15:'header_probe',16:'phase_probe'}
signed=lambda n:n if n<2**31 else n-2**32
def analyze(text,base,size):
 r=parse(text);calls=r['calls'];main={i:c for i,c in calls.items() if base<=c['ret']<base+size}
 assert not any(c['api'] in [14,15,16] for c in calls.values())
 assert len(r['phase_rows'])==1 and r['phase_rows'][0][0]==1 and r['phase_ends'][0][0]==1
 assert any(c['api']==11 and c['phase']==1 for c in main.values()),'no park-phase RCT presentation sample'
 created={};rows=[];formats=[]
 for i,c in main.items():
  api=c['api']
  if api<3:continue
  row=dict(id=i,api=NAMES[api],phase=c['phase'],args=r['args'][i],result=c['result'])
  if i in r['outputs']:row['output_pointer']=r['outputs'][i]
  if api==4 and c['result'] and r['outputs'][i]:created[r['outputs'][i]]=i
  if i in r['dibs']:
   d=r['dibs'][i];row['header']=d
   if d['status']==0:
    raw=d['raw'];fmt=dict(width=signed(raw[1]),height=signed(raw[2]),planes=raw[3]&65535,bpp=raw[3]>>16,compression=raw[4],size_image=raw[5],colors_used=raw[8],stride=d['stride'],extent=d['extent'])
    row['format']=fmt
    if fmt not in formats:formats.append(fmt)
  if api==11:row['bits_created_by_sample']=created.get(r['args'][i][9])
  rows.append(row)
 return dict(passed=True,total_pairs=len(calls),main_pairs=len(main),other_pairs=len(calls)-len(main),all_call_counts=dict(Counter(NAMES[c['api']] for c in calls.values())),main_call_counts=dict(Counter(NAMES[c['api']] for c in main.values())),
  phases=r['phase_rows'],pending=r['pending_rows'],phase_end=r['phase_ends'],
  rct_stretch_per_phase=[sum(c['api']==11 and c['phase']==p for c in main.values()) for p in [0,1]],
  caps=[dict(api=NAMES[a],phase=p,recorded=n,address=addr) for (a,n,addr),p in zip(r['caps'],r['cap_phases'])],
  formats=formats,graphics=rows,modules=r['modules'],
  limits='Instrumented PC samples with32 StretchDIBits entries per phase and32 for other graphics APIs overall. Not frames, timings, pixel allocation accessibility, palette content or Xbox GPU evidence.')
