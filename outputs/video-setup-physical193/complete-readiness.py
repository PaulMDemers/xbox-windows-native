"""Complete current NT5 provider/dependency pins before any physical write or launch."""
import hashlib,importlib.util,json,ast
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'readiness-completion.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ready=read(k/'physical-ready.json')
for n,v in ready['source_pins'].items():assert sha(k/n)==v
for n,v in ready['input_pins'].items():assert sha(ws/n)==v
assert read(k/'audit-parser-tests.json')['passed'] and read(k/'audit-parser-tests.json')['source_sha256']==sha(k/'audit-physical.py')
for n in ['physical-ready','capture']:
 p=k/(n+'001.json');assert not p.exists();p.write_bytes((k/(n+'.json')).read_bytes())
spec=importlib.util.spec_from_file_location('capture_helpers',ws/'outputs/fatx0098-soak3/physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
review=read(ws/'outputs/video-setup-preflight190/build-review.json');capture=read(k/'capture.json');providers=[]
with m.connect() as f:
 m.owner(f)
 for name,row in review['providers'].items():
  path='/F/winnt/system32/'+name;data=m.get(f,path);assert hashlib.sha256(data).hexdigest()==row['sha256'];assert m.get(f,path)==data
  p=k/'artifacts'/path.lstrip('/');assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  item=dict(path=path,bytes=len(data),sha256=row['sha256'],expected_last_physical_sha256=row['sha256'],matches_last_physical=True,second_read_exact=True,supplemental_actual_nt5_provider=True);capture['files'].append(item);providers.append(item)
capture['provider_supplement']='Complete-readiness added actual matching NT5 imported/dynamic providers; original capture001 and physical-ready001 retained. Read-only, no physical writes or launch.'
(k/'capture.json').write_text(json.dumps(capture,indent=2)+'\n')
inputs=[k/'capture.json',k/'physical-ready001.json',k/'capture001.json',k/'audit-parser-tests.json',k/'DESIGN.md',ws/'outputs/video-setup-preflight190/build-review.json',ws/'outputs/fatx0098-soak3/physical.py',ws/'outputs/release-0.1.0/release.json',ws/'outputs/native-windows-physical-f/decode-legacy-events.py',ws/'outputs/native-windows-nt5-kernel/nt5_hive_indexes.py']
inputs += [k/'artifacts'/r['path'].lstrip('/') for r in capture['files']]
for p in inputs:ready['input_pins'][p.relative_to(ws).as_posix()]=sha(p)
ready['source_pins'][Path(__file__).name]=sha(Path(__file__))
ready['readiness_completion']='Actual NT5 providers and captured bytes/dependencies/parser tests pinned; preliminary capture/readiness retained. No source or gate relaxed, no physical write/launch.'
(k/'physical-ready.json').write_text(json.dumps(ready,indent=2)+'\n')
dest.write_text(json.dumps(dict(passed=True,physical_access=True,physical_writes=False,launch_performed=False,providers=providers,preliminary_ready_sha256=sha(k/'physical-ready001.json'),ready_sha256=sha(k/'physical-ready.json')),indent=2)+'\n')
print('Actual four NT5 providers/current captured bytes/dependencies pinned; no physical write/launch')
