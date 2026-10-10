"""Read-only final216 pins and closed unique ordinary pair; no collection repeats."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'evidence-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'));pins={}
def pin(p,h):
 assert sha(p)==h,str(p);pins[str(p)]=h
for n,h in read(k/'emulator-frozen.json').items():pin(ws/n,h)
assert read(k/'emulator-pair-review.json')['passed'] and read(k/'state-observations.json')['passed']
assert read(k/'interpret-tests.json')['cases']==4096
pin(k/'interpret-state.py',read(k/'interpret-tests.json')['interpreter_sha256'])
for name,row in read(k/'handoff-inventory.json')['files'].items():pin(k/'artifacts/handoff002'/name,row['sha256'])
for n,row in read(k/'handoff-inventory.json')['binaries'].items():
 if 'private_copy' in row:pin(k/row['private_copy'],row['sha256'])
pin(k/'artifacts/handoff002/binaries/LoadReactOS.o',read(k/'handoff-inventory.json')['binaries']['launcher-object']['sha256'])
for n,h in read(k/'model-inventory.json')['source_pins'].items():pin(k/'artifacts/model002'/n,h)
for row in read(k/'references.json')['references']:pin(k/'artifacts/references'/row['name'],row['sha256'])
for n,h in read(k/'source-review.json')['source_pins'].items():pin(k/n,h)
for name,h in read(k/'inventory001-failures.json')['partial_artifacts'].items():pin(k/name,h)
for row in read(k/'source-review001-failure.json')['changes']:pin(k/'artifacts/initial-adapters'/row['name'],row['initial_sha256'])
for row in read(k/'inventory001-failures.json')['failures']:pin(k/row['source'],row['sha256'])
for name in ['control001','candidate001']:
 out=k/('emu-'+name);a=read(out/'audit.json');c=read(out/'closure.json');host=read(out/'host-state.json')
 assert host['closed'] and c['closed'] and c['never_relaunch_or_recollect']
 assert a['scoped_display_passed'] and not a['strict_qualification_passed']
 assert a['gpu_snapshot']['actual_new_reads']==(52 if name=='candidate001' else 0)
 assert a['gpu_snapshot']['missed']==0 and a['normal_shutdown_count']==1 and a['dashboard_return']
 assert [(e['source'],e['event_id']) for e in a['warnings_errors']]==[('Ftdisk',49)]
 pin(out/'audit.json',c['audit_sha256']);pin(out/'artifacts/after-xwn-video-trace.bin',a['gpu_snapshot']['sha256'])
 f=read(k/('fixture-'+name+'.json'));pin(Path(f['fixture_path_windows']),f['seed_sha256'])
 run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/gstate216-runs/nt5-gstate216-'+name)
 pin(run/'cleanup.json',c['cleanup_sha256']);assert read(run/'cleanup.json')['completedUtc']
 assert host['runner_exit_code']==0 and host['observer_exit_code']==0 and host['audit_exit_code']==0
 pin(run/'instance.json',host['instance_sha256'])
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),checked_pins=len(pins),pins=pins,
 all_owned216_sessions_closed=True,ordinary_pair_scoped_passed=True,strict_qualification_passed=False,
 physical_access=False,gpu_submission=False,
 limits='Actual cold/trace/source/cleanup pins; no recollection,context grant,physical performance or wholeboot qualification. Ftdisk49 remains strict failure; prelaunch source harness failures preserved.'),indent=2)+'\n',encoding='utf-8')
print('Closed216 evidence PASS:',len(pins),'pins')
