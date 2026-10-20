"""Cached timer-control location interpretation, not CPU-time percentages."""
from pathlib import Path
from collections import Counter
import hashlib,json
K=Path(__file__).resolve().parent;out=K/'location-review001.json';assert not out.exists()
read=lambda n:json.loads((K/n).read_text())
r=read('review001.json');assert r['passed']
seed=json.loads((K.parent/'rct621/seed-symbols001.json').read_text());assert seed['passed']
symbols=json.loads((K.parent/'rct621/site-symbols001.json').read_text());assert symbols['passed']
manifest=json.loads(Path('C:/xwn622/pc001/cold1-002/manifest.json').read_text())
for f in seed['files']:
 assert manifest['winnt/system32/'+f['name']]['sha256']==f['sha256']
 p=Path(f['path'].replace('/mnt/c/','C:/'));assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
log=read('raw-control-logs001.json')['sampler'];mods={};counts={i:Counter() for i in range(4,8)}
for line in log.splitlines():
 v=line.split()
 if v[0]=='MODULE':mods.setdefault(int(v[1]),[]).append((int(v[2],16),int(v[3],16),' '.join(v[4:]).lower().split(chr(92))[-1]))
 if v[0]=='SAMPLE':
  i=int(v[1]);ip=int(v[4],16);owner=[(b,n) for b,s,n in mods[i] if b<=ip<b+s];assert len(owner)==1
  base,name=owner[0];off=ip-base;label='module offset only'
  if name=='winmm.dll' and 0x7bbc<=off<0x7bfd:label='timeGetTime body'
  elif name=='winmm.dll' and 0x7bfd<=off<0x7c45:label='direct arithmetic helper of timeGetTime'
  elif name=='ntdll.dll' and off==0x8ce7:label='NtSetInformationThread syscall return'
  counts[i][name,hex(off),label]+=1
rows={str(i):[dict(module=m,offset=o,label=l,samples=n) for (m,o,l),n in c.most_common()] for i,c in counts.items()}
for i,c in counts.items():assert sum(c.values())==r['cases'][str(i)]['samples']
out.write_text(json.dumps(dict(passed=True,cases=rows,exact_protected_DLLs_match621=True,
 scope='Reuses exact621 on-disk export/instruction analysis. No runtime code bytes or kernel stacks; location counts are not CPU-time fractions, wait durations, or game FPS.'),indent=2)+'\n')
print('Cached observed timer locations decoded against exact protected DLL identities')
