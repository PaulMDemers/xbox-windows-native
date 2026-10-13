"""Additional cross-packet identity proof; does not rewrite frozen audit/decoder."""
import importlib.util,struct
from pathlib import Path
spec=importlib.util.spec_from_file_location('joined_memory360',Path(__file__).resolve().parent.parent/'memory-analysis360/decode.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REC=33344
def join(bandwidth,actual):
 a=m.decode(actual,warm=True);w=struct.unpack('<133392I',bandwidth)
 m.need(w[:5]==(0x42575758,364,533568,4,15),'complete bandwidth')
 real={v['physical'] for v in a['rows']};result=[]
 for slot in range(4):
  r=w[16+slot*REC:16+(slot+1)*REC]
  m.need((r[4],r[5],r[6])==(a['owner'],a['shadow'],a['scanout']),'actual PDEV/source/destination identity')
  p=r[12];n=2073600;m.need(p+n<=0xffffffff,'scratch wrap')
  for base in [a['shadow'],a['scanout']]:m.need(p+n<=base or base+a['bytes']<=p,'scratch overlaps live allocation')
  for phase in (0,1):
   b=m.decode(struct.pack('<16640I',*r[64+phase*16640:64+(phase+1)*16640]))
   m.need(b['shadow']==p and b['scanout']==a['scanout'],'private mapping identity')
   private={v['physical'] for v in b['rows'] if v['role']==0}
   m.need(not private&real,'scratch physical alias with full primary/scanout')
  result.append(dict(slot=slot,matched=True))
 return dict(passed=True,records=result,scope='Additional cross-packet identity/full-shadow physical-disjointness check. Endpoint records, not global aliases or transient ABA proof.')
