from pathlib import Path
import sys,json,hashlib
K=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/windows480p634');W=K.parents[1]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,STARTUP
S=Path('/mnt/c/xwn466/preparation001/seed.qcow2')
sha=lambda b:hashlib.sha256(b).hexdigest()
f=json.loads((W/'outputs/marker-handoff466/preparation001.json').read_text());assert f['seed_never_executed'];assert hashlib.file_digest(S.open('rb'),'sha256').hexdigest()==f['seed_sha256']
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
rows={}
with ColdIO(S) as io:
 wr=m.Writer(io,m.fatx.open_partition(io,S,'E'))
 for n in ['Applications/XWNEBoot/default.xbe','Applications/XWNEBoot/freeldr.sys','Applications/XWNEBoot/freeldr.ini','Applications/XWNEBoot/loader/halxboxnt5.dll','winnt/system32/drivers/xboxvnt5.sys','winnt/system32/xwnown.dll','winnt/system32/bootvid.dll','winnt/system32/xwn-video-trace.bin',STARTUP]:
  try:b=wr.read(n)
  except KeyError:rows[n]=dict(present=False);continue
  rows[n]=dict(present=True,bytes=len(b),sha256=sha(b))
  if n.endswith(('.cmd','.ini')):print(n,repr(b))
(K/'seed-inventory002.json').write_text(json.dumps(dict(seed=str(S),seed_sha256=f['seed_sha256'],never_executed=True,files=rows),indent=2)+'\n')
print(json.dumps(rows,indent=2))
