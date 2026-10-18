"""Close all new evidence; no launch, retry or physical access."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def local(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
r=dict(passed=False,physical_access=False,physical_candidate_qualified=False,ordinary_boot_qualified=False,strict=False)
try:
 runs=[];captures=0;frozen=0
 for n in [1,2,3]:
  o=K/f'emu{n:03d}';a=json.loads((o/'audit.json').read_text());t=json.loads((o/'trace.json').read_text())
  assert a['host_exit']['passed'] and a['eeprom_unchanged'] and a['source_unchanged']
  assert a['allocation']['allocation_consistent'] and not a['qcow_check'].get('check-errors',0)
  for p,h in json.loads((o/'frozen.json').read_text()).items():assert sha(W/p)==h,p;frozen+=1
  for p,h in json.loads((o/'host-dependencies.json').read_text()).items():assert sha(Path(p))==h,p
  for v in t['reads']:assert sha(Path(v['private_file']))==v['sha256'];captures+=1
  for p,h in a['private_cold_files'].items():assert sha(local(p))==h,p
  runs.append(dict(id=n,scope_pass=t['passed'],changed_bytes=a['changed_bytes'],host_exit=0,
                   cleanup_error=t.get('cleanup_error'),breakpoints_remaining_before_exit=t.get('remaining_breakpoints'),
                   source_unchanged=True,allocation_clean=True))
 assert runs[0]['scope_pass']==runs[1]['scope_pass']==False and runs[2]['scope_pass']==True
 a=json.loads((K/'emu003/actual-controls.json').read_text());assert a['passed']
 p=json.loads((K/'emu003/protected.json').read_text());assert p['passed']
 for n in ['host001','stub-host001']:
  h=json.loads((K/(n+'.json')).read_text());assert h['status']=='passed'
  for f,v in h['files'].items():assert sha(local(f))==v['sha256']
 b=json.loads((K/'build001.json').read_text())
 for f,v in b['files'].items():assert sha(local(f))==v['sha256']
 for n in ['preparation001','preparation002']:
  q=json.loads((K/(n+'.json')).read_text());assert q['status']=='prepared' and sha(local(q['seed']))==q['seed_sha256']
 q=json.loads((K/'preparation001.json').read_text())
 for f,h in q['parent_chain'].items():assert sha(local(f))==h
 r.update(passed=True,runs=runs,frozen_input_checks=frozen,captured_memory_files_rehashed=captures,
          actual_marker_negative_cases=a['actual_marker_mutations_rejected'],protected_byte_exact_files=len(p['files']),
          no_installed_physical_change=True,next='watched physical diagnostic after physical staging/recovery review',
          failed_emu002_stop_label_invalid_see_errata=True)
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
