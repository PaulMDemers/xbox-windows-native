"""Independent frozen bytes, result scope, source findings and repository review."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
inv=read(k/'inventory001.json');host=read(k/'host001.json')
assert inv['passed'] and host['passed'] and not inv['plan_allowed']
assert not inv['guest_launch'] and not inv['physical_access'] and host['native_grants']==0
assert sha(k/'inventory.py')==inv['source_sha256'] and sha(k/'run-host.py')==host['source_sha256']
assert sha(ws/'outputs/video-loader-handoff225/evidence-review.json')==inv['prior225_evidence_sha256']
manifest=ws/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json'
assert sha(manifest)==inv['compiled_manifest_sha256'];pins=read(manifest)
for rel,h in dict(inv['unchanged_original_sources'],**inv['prior_reconstructed_candidate_sources']).items():
 assert sha(k/'artifacts/source'/rel)==h==pins[rel],rel
for name,h in host['pins'].items():assert sha(k/name)==h==sha(k/'artifacts/host001'/name),name
for row in host['runs']:
 assert row['compile_exit']==row['exit_code']==0 and not row['stderr']
 assert row['stdout']=='checks=368513 synthetic_cycles=4096 inherited_overlap_cases=100000 private_overlap_cases=100000 native_grants=0\n'
 assert sha(Path(row['command'][-1].replace('/mnt/c/','C:/')))==row['binary_sha256']
assert host['native_compile']['exit_code']==0 and not host['native_compile']['undefined_symbols']
assert sha(k/'artifacts/host001/owner-i686.o')==host['native_compile']['object_sha256']
e=read(ws/'outputs/video-loader-handoff225/evidence-review.json');s=e['states'][-1]
assert inv['ramfc']['raw']==s['ramfc_raw'] and inv['ramro']['raw']==s['ramro_raw']
assert len(s['ramht']['valid_entries'])==inv['old_ramht']['valid_entries']==22
assert not inv['ramfc']['extent_verified'] and not inv['ramro']['extent_verified']
text=(k/'owner.c').read_text();assert text.index('o->exposed=1')<text.index('o->pending_action=action')
assert 'o->plan=*p;' in text and 'X226_COMPLETED' in text and 'X226_RESTORE:expected=X226_DRAINING' in text
syntax=[]
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p));syntax.append(p.name)
files=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0');staged={}
for name in files:
 if name.startswith('outputs/video-owner-transition226/'):
  data=subprocess.check_output(['git','show',':'+name],cwd=ws);assert data==(ws/name).read_bytes()
  assert '/artifacts/' not in name;staged[name]=hashlib.sha256(data).hexdigest()
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 source_sha256=sha(Path(__file__)),staged_byte_pins=staged,python_syntax=syntax,matched_model_sources=12,
 host_scope_only=True,guest_launch=False,physical_access=False,gpu_ownership_qualified=False,
 limits='Reducer ordering and compile compatibility only; actual225 preparation refused. No runtime adapter, backend retirement or GPU acceleration qualified. Review self/output staged afterward.'),indent=2)+'\n')
print('226 independent bytes/scope/source/repository review PASS')
