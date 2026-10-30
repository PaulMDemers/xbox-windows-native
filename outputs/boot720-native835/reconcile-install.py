"""Reconcile immutable create/readback journal before allowing boot executables. No FTP."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn835/install001');out=K/'installation-review001.json';assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
s=read(K/'installation001.json');pkg=read(K/'package001.json')
assert s['state']=='payload_installed' and not s['windows_launch_requested'] and not s['boot_executables_present']
assert s['source_sha256']==sha((K/'install001.py').read_bytes()) and s['package_sha256']==sha((K/'package001.json').read_bytes())
raw=(P/'writes.jsonl').read_bytes();assert raw.endswith(b'\n');rows=[json.loads(x) for x in raw.splitlines()];assert len(rows)%2==0
dirs=[];files={}
for a,b in zip(rows[::2],rows[1::2]):
 assert a['path']==b['path'] and a['meta']==b['meta']
 if a['kind']=='mkdir_intent':
  assert b['kind']=='mkdir_done' and a['meta'] is None;dirs.append(a['path'])
 else:
  assert a['kind']=='write_intent' and b['kind']=='write_verified'
  assert a['path'] not in files;files[a['path']]=a['meta']
assert len(dirs)==len(set(dirs)) and set(dirs)==set(pkg['directories'])
expected={p:{k:v[k] for k in ['bytes','sha256']} for p,v in pkg['files'].items()};assert files==expected
assert len(files)==s['verified_files']==6563 and sum(v['bytes'] for v in files.values())==s['verified_bytes']
r={'passed':True,'physical_access':False,'basis':'Every create intent paired with exact readback verification in the one physical upload journal; directory baseline audit passed at completion','installation_record_sha256':sha((K/'installation001.json').read_bytes()),'journal_sha256':sha(raw),'files':len(files),'directories':len(dirs),'verified_bytes':s['verified_bytes'],'overwrites':0,'windows_launch_requested':False}
out.write_text(json.dumps(r,indent=2)+'\n')
assert read(K/'hive-review002.json')['passed']
# Freeze actual controller, source and qualification bytes. Later receipts are separate.
pins={p.name:sha(p.read_bytes()) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','source002.json','chain002.json','qualify001.json','host006.json','cpu-build010.json','cpu-run010.json','build001.json','package001.json','installation001.json','installation-review001.json','hive-review002.json'])}
(K/'launch-source-pins001.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Installation journal reconciled:',len(files),'files,',s['verified_bytes'],'bytes; boot staging admitted')
