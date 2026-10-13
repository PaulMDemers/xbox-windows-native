"""Independent364 packet reader. No native/physical access."""
import hashlib,importlib.util,struct
from pathlib import Path
_spec=importlib.util.spec_from_file_location('memory360',Path(__file__).resolve().parent.parent/'memory-analysis360/decode.py');_m=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_m)
ROWS=16640;REC=64+2*ROWS;BYTES=4*(16+4*REC)
def need(ok,s):
 if not ok:raise ValueError(s)
def q(w,i):return w[i]|w[i+1]<<32
def decode(data):
 need(len(data)==BYTES,'length');w=struct.unpack('<%dI'%(BYTES//4),data)
 need(w[:5]==(0x42575758,364,BYTES,4,15) and not any(w[5:16]),'header/coverage')
 result=[]
 for slot in range(4):
  r=w[16+slot*REC:16+(slot+1)*REC]
  need(r[:4]==(364,slot,0,slot&1),'record/status/order')
  need(all(r[i]>=0x80000000 for i in (4,5,6,12)),'owners')
  need(r[8:12]==(7680,2560,360,921600),'geometry')
  y,x=divmod(r[7],7680);need(x%4==0 and x<=5120 and y<=720,'rectangle')
  need(r[13]==0 and 0<q(r,14)<=10000000000,'exception/frequency')
  need(r[24]==32 and q(r,25)<=q(r,27)<1<<63,'calibration')
  need(r[29:33]==(0,0,0,1) and not any(r[33:64]),'pixels/guards/cleanup/reserved')
  a,b,c,d=[q(r,i) for i in (16,18,20,22)]
  need(0<=a<b<1<<63 and 0<=c<d<1<<63,'timing')
  need(b<=c if slot%2==0 else d<=a,'actual order')
  before,after=[_m.decode(struct.pack('<16640I',*r[64+j*ROWS:64+(j+1)*ROWS])) for j in (0,1)]
  for v in (before,after):
   need(v['owner']==r[4] and v['shadow']==r[12] and v['scanout']==r[6] and v['bytes']==2073600,'mapping identity')
   need(set(v['counts']['shadow'])=={'WB'} and set(v['counts']['scanout'])=={'UC'},'effective private/scanout policy')
   need(all(t['physical']<0x03700000 for t in v['rows'] if t['role']==0),'private RAM outside reservation')
   for t in v['rows']:
    if t['role']==1:need(t['physical']==0x03700000+((t['virtual']-(r[6]&~4095))),'scanout physical mapping')
  need(r[80:160]==r[64+ROWS+16:64+ROWS+96],'CPU state across pair')
  aa=[(v['role'],v['virtual'],v['physical'],v['pde']&~0x60,v['pte']&~0x60) for v in before['rows']]
  bb=[(v['role'],v['virtual'],v['physical'],v['pde']&~0x60,v['pte']&~0x60) for v in after['rows']]
  need(aa==bb,'translation changed')
  f=q(r,14);result.append(dict(slot=slot,ram_first=not(slot&1),bytes=r[11],ram_ticks=b-a,scanout_ticks=d-c,frequency=f,
   ram_ms=(b-a)*1000/f,scanout_ms=(d-c)*1000/f,calibration_min=q(r,25),calibration_max=q(r,27),offset=r[7],
   ram_counts=before['counts']['shadow'],scanout_counts=before['counts']['scanout'],mapping_rows=len(aa)))
 return dict(passed=True,records=result,sha256=hashlib.sha256(data).hexdigest(),performance_qualified=False,
  scope='Four bounded instrumented real upload calls; private RAM copy vs existing scanout copy; endpoints not all-alias/TLB or normal desktop performance')
