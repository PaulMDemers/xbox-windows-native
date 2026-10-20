"""Source, binary and media pins; closed runtimes are never opened."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
out=K/'inheritance-review002.json';assert not out.exists()
b=json.loads((K/'build002.json').read_text());assert b['status']=='compiled'
rows={}
for path,v in b['files'].items():
 p=host(path);assert sha(p)==v['sha256'],path
 if p.suffix in ['.c','.h'] and p.name!='target_iat.h':
  assert p.read_bytes()==(K/p.name).read_bytes(),p.name
 rows[path]=v['sha256']
for name,h in json.loads((K/'host-tests001.json').read_text())['sources'].items():
 assert sha(K/name)==h,name
for path,h in json.loads((K/'ntfs-preparation001.json').read_text())['inputs'].items():
 assert sha(host(path))==h,path
for n in ['calls.h','phase.h','lifetime.h','dib_header.h','trace_oracle.py','dib_oracle.py']:
 assert (K/n).read_bytes()==(K.parent/'rct610'/n).read_bytes(),n
for n in ['serial_host.py','input_transport001.py','actions002.py','login001.py','cold002.py','event_timestamps002.py','process_review001.py']:
 old=(K.parent/'rct614'/n).read_text()
 for prefix in ['xwn','XWN','rct','run','RUN']:old=old.replace(prefix+'614',prefix+'616')
 old=old.replace("'614'","'616'")
 assert old==(K/n).read_text(),n
failed=json.loads((K/'build001.json').read_text());assert failed['status']=='failed'
assert (K/'subject-build001.c').read_bytes()==Path('C:/xwn616/build001/subject.c').read_bytes()
out.write_text(json.dumps(dict(passed=True,build_files=rows,host_and_preparation_pins=True,
 unchanged_core610=True,namespace_helpers614=True,failed_build001_preserved=True),indent=2)+'\n')
print('616 exact built source, frozen helper and failed-build pins passed')
