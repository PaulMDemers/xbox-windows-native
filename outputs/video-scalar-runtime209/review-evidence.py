"""Review closed209 source/input/ordinary/physical evidence; no console access."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'evidence-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checked=0
def pins(base,rows):
 global checked
 for n,h in rows.items():assert sha(base/n)==h,n;checked+=1
pins(ws,read(k/'emulator-frozen.json'))
ready=read(k/'physical-ready.json');pins(k,ready['source_pins']);pins(ws,ready['input_pins'])
for filename in ['parser-tests.json','row-parser-tests.json']:
 r=read(k/filename);assert r['passed'];pins(k,r['source_pins']);pins(k,r['input_pins'])
parent=k.parent/'video-text-clip205';pins(parent/'display',read(parent/'source-review.json')['source_files'])
build=k.parent/'video-scalar208';assert read(build/'build-review.json')['passed'] and read(build/'instruction-review.json')['passed']
assert read(build/'fresh-control-normalized-comparison.json')['passed']
package=read(k/'package-review.json');pins(k/'artifacts',package['helpers'])
cases={}
for name in ['control001','candidate001']:
 emu=k/('emu-'+name);a=read(emu/'audit.json');c=read(emu/'closure.json');host=read(emu/'host-state.json')
 assert c['closed'] and c['audit_sha256']==sha(emu/'audit.json') and a['scoped_display_passed'] and a['integrity_passed']
 assert host['closed'] and host['status']=='cold_audited_closed' and host['source_sha256']==sha(k/'run-emulator.py')
 for refusal in host['resource_attempts']:
  assert refusal['resource_busy'] and not refusal['runner_start_exists'] and not refusal['run_exists']
  assert sha(emu/('resource-attempt%d-console.txt'%refusal['attempt']))==refusal['log_sha256'];checked+=1
 launch=read(emu/'launch.json');assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return']
 out=k/name;c=read(out/'closure.json');assert c['closed'] and c['scoped_display_passed'] and c['baseline_restored'] and not c['startup_enabled']
 pins(out,c['evidence_pins']);state=read(out/'physical.json')
 for group in ['before','after','before_payloads']:
  for row in state[group].values():
   if row:assert sha(ws/row['path'])==row['sha256'];checked+=1
 finish=read(out/'finish-state.json');assert finish['closed'] and finish['status']=='collected_restored_audited_closed'
 assert all(v['exit_code']==0 for v in finish['steps'])
 assert (out/'physical-hive-audit.json').exists() and read(out/'physical-hive-audit.json')['passed']
 assert read(out/'restored-verification.json')['passed']
 cases[name]=dict(physical_closure_sha256=sha(out/'closure.json'),ordinary_closure_sha256=sha(emu/'closure.json'),
  host_state_sha256=sha(emu/'host-state.json'),finish_state_sha256=sha(out/'finish-state.json'))
for name in ['emulator-pair-review.json','physical-pair-review.json']:assert read(k/name)['passed']
old=k.parent/'video-word-physical187';assert not (old/'candidate001/physical.json').exists()
r=dict(passed=True,checked_pins=checked,cases=cases,source_sha256=sha(Path(__file__)),baseline_restored=True,physical_access=False,
 actual_scalar_coverage_passed=True,only_definition_difference='XWN_UC_STORES',text_bounds_and_body_clocks_off_both=True,
 strict_whole_boot_qualified=False,full_storage_qualified=False,release_qualified=False,
 limits='Source/hash/closure review of actual recorded narrow scopes. No new launch, collection or timing/FPS inference. Known Ft49 remains strict failure;187 never-launched candidate remains preserved.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
