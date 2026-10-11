"""Parse complete bounded scalar groups; never infer pixel correctness."""
import collections,hashlib,json,re,sys
from pathlib import Path
RX=re.compile(r'^nv2a_lifecycle244 phase=(\d+) when=(\d+) thread=(\d+) ref=(\d+) a=(\d+) b=(\d+)$')
SITES={1:'overlap',2:'age',3:'cpu-write-eviction',4:'incompatible',5:'flush',6:'common-entry',11:'cpu-read',12:'cpu-write'}
def parse(data):
 assert len(data)<=32*1024**2 and data.endswith(b'\n')
 groups={};limits=[]
 for line in data.decode('utf-8').splitlines():
  if not line.startswith('nv2a_lifecycle244 '):continue
  m=RX.fullmatch(line);assert m,'Malformed lifecycle line'
  event,when,thread,seq,a,b=map(int,m.groups())
  if event==99:assert seq in SITES and a==256;limits.append(seq)
  if not 100<=event<=106:continue
  assert seq>0 and thread>0 and len(groups)<2049
  g=groups.setdefault(seq,dict(when=when,thread=thread,parts={}))
  assert g['when']==when and g['thread']==thread and event not in g['parts']
  g['parts'][event]=[a,b]
 assert groups,'No257 telemetry'
 rows=[];counts=collections.Counter()
 for seq,g in sorted(groups.items()):
  p=g['parts'];assert set(p)==set(range(100,107)),'Incomplete group'
  site,flags=p[100];assert site in SITES and 0<=flags<16
  counts[site]+=1;assert counts[site]<=256
  rows.append(dict(sequence=seq,when=g['when'],thread=g['thread'],site=site,reason=SITES[site],flags=flags,surface=p[101][0],callback=p[101][1],address=p[102][0],size=p[102][1],texture=p[103][0],binding_bits=p[103][1],primitive=p[104][0],arrays=p[104][1],inline_array=p[105][0],inline_elements=p[105][1],inline_buffer=p[106][0],framebuffer_in_use=p[106][1]))
 return dict(groups=len(rows),sites={str(s):dict(reason=SITES[s],count=counts[s],draw_dirty=sum(r['site']==s and bool(r['flags']&1) for r in rows),upload_pending=sum(r['site']==s and bool(r['flags']&8) for r in rows)) for s in SITES},truncated_sites=limits,rows=rows,pixel_preservation_proved=False,physical_access=False,ordinary_qualified=False)
if __name__=='__main__':
 k=Path(__file__).resolve().parent;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase257-runs/nt5-phase257-preserve001');out=k/'preserve001/site-observation.json';assert not out.exists()
 assert json.loads((k/'preserve001/host-state.json').read_text())['closed']
 raw=run/'cpu-trace.log';data=raw.read_bytes();r=parse(data);r['raw_sha256']=hashlib.sha256(data).hexdigest();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['groups','sites','truncated_sites']},indent=2))
