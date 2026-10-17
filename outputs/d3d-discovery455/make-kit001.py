"""Fresh NT5 inventory fixture; preserve closed lifecycle inputs."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'lifecycle453'
def rep(s,a,b):assert a in s,a;return s.replace(a,b)
names=['prepare001.py','cold002.py','cold003.py','login001.py','run001.py','preflight001.py','independent001.py','binary-review001.py','build001.py','runner.c','review001.py','closeout001.py']
for name in names:
 s=(old/name).read_text(encoding='utf-8').replace('lifecycle453','d3d-discovery455').replace('453','455').replace('graphics_lifecycle','graphics_discovery').replace('lifecycle.c','discovery.c').replace('lifecycle.cmd','discovery.cmd').replace('life.exe','d3d.exe').replace('LIFE.EXE','D3D.EXE').replace('r05d','r06d').replace('r05s','r06s').replace('-pixels.bin','-caps.bin')
 if name=='preflight001.py':
  s=rep(s,",K/'modules001.json'",'')
  s=rep(s,"assert manifest['winnt/system32/psapi.dll']['sha256']==json.loads((K/'modules001.json').read_text())['psapi_sha256']", "prior=json.loads((K.parent/'lifecycle453/independent001.json').read_text());assert manifest['winnt/system32/ddraw.dll']['sha256']==next(r['sha256'] for r in prior['rows'] if r['path']=='winnt/system32/ddraw.dll')")
 if name=='independent001.py':s=rep(s,",'psapi.dll'",'')
 if name=='build001.py':
  s=rep(s,'d3d-discovery455-build001','discovery455-build001').replace("sample/'lifecycle.exe'","sample/'discovery.exe'")
 if name=='closeout001.py':
  s=s.replace('scoped_lifecycle_passed','scoped_inventory_passed')
  s=rep(s,"exact_bytes=sum(row['review']['exact_bytes'] for row in r['rows'] if 'review' in row)","capability_bytes=sum(236*row['review']['device_count'] for row in r['rows'] if 'review' in row)")
  s=s.replace("record['exact_bytes']","record['capability_bytes']").replace("'exact bytes;'","'capability bytes;'")
  s=s.replace("'Raw SYSTEMMEMORY bytes, no scanout/GPU/performance qualification','No actual loss/Restore path','Calling-thread focus only','Bounded process commitment, not leak freedom'","'Capability declarations only; no CreateDevice/draw/GPU proof'")
 if name=='review001.py':s=s.replace('Actual NT5 PC system-memory churn; thread-local focus only; real loss/restore unqualified','Actual NT5 D3D7 capability inventory; no CreateDevice or rendering')
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
for name in ['launch_gate.py','inherited-gate-tests001.json']:
 p=K/name;assert not p.exists();p.write_bytes((old/name).read_bytes())
rows={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.py')}
(K/'kit-review001.json').write_text(json.dumps(dict(rows=rows,scope='Two-case unchanged-mode control adapted from453 for D3D inventory; original launch gate byte-exact'),indent=2)+'\n')
