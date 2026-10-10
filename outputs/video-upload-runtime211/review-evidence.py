"""Read-only closed211 source/input/ordinary/physical evidence verification."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'evidence-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checked=0

def pins(base,rows):
 global checked
 for name,digest in rows.items():assert sha(base/name)==digest,name;checked+=1

# Four description-only changes occurred after ordinary closure. Verify the
# original ordinary pins against their preserved bytes, not rewritten manifests.
correction=read(k/'physical-scope-correction.json');assert correction['passed']
for name,digest in read(k/'emulator-frozen.json').items():
 p=ws/name
 if p.parent==k and p.name in correction['changes']:
  row=correction['changes'][p.name]
  assert digest==row['before_sha256']==row['archive_sha256']
  assert sha(ws/row['ordinary_source_archive'])==digest and sha(p)==row['after_sha256']
  assert (ws/row['ordinary_source_archive']).read_text().replace(row['literal_before'],row['literal_after'])==p.read_text()
 else:assert sha(p)==digest,name
 checked+=1
ready=read(k/'physical-ready.json');pins(k,ready['source_pins']);pins(ws,ready['input_pins'])
for filename in ['parser-tests.json','upload-parser-tests.json','sequence-parser-tests.json']:
 r=read(k/filename);assert r['passed'];pins(k,r['source_pins'])
 if 'input_pins' in r:pins(k,r['input_pins'])
build=k.parent/'video-upload-accounting210'
pins(build/'display',read(build/'source-review.json')['source_files'])
for filename in ['build-review.json','instruction-review.json','host-tests001.json','source-manual-review.json']:
 assert read(build/filename)['passed'],filename
pins(build,read(build/'host-tests001.json')['source_pins'])
package=read(k/'package-review.json');pins(k/'artifacts',package['helpers'])
for rows in package['cases'].values():
 for row in rows:assert sha(ws/row['source'])==row['sha256'];checked+=1
cases={}
for name in ['control001','candidate001']:
 emu=k/('emu-'+name);a=read(emu/'audit.json');c=read(emu/'closure.json');host=read(emu/'host-state.json')
 assert c['closed'] and c['audit_sha256']==sha(emu/'audit.json') and a['scoped_display_passed'] and a['integrity_passed']
 assert host['closed'] and host['status']=='cold_audited_closed' and host['source_sha256']==sha(k/'run-emulator.py')
 for refusal in host['resource_attempts']:
  assert refusal['resource_busy'] and not refusal['runner_start_exists'] and not refusal['run_exists']
  assert sha(emu/('resource-attempt%d-console.txt'%refusal['attempt']))==refusal['log_sha256'];checked+=1
 launch=read(emu/'launch.json');assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return']
 out=k/name;c=read(out/'closure.json');state=read(out/'physical.json')
 assert c['closed'] and c['scoped_display_passed'] and c['baseline_restored'] and not c['startup_enabled']
 pins(out,c['evidence_pins'])
 for group in ['before','after','before_payloads']:
  for row in state[group].values():
   if row:assert sha(ws/row['path'])==row['sha256'];checked+=1
 finish=read(out/'finish-state.json');assert finish['closed'] and finish['status']=='collected_restored_audited_closed'
 assert all(v['exit_code']==0 for v in finish['steps'])
 assert read(out/'physical-hive-audit.json')['passed'] and read(out/'restored-verification.json')['passed']
 for root in [emu,out]:
  seq=read(root/'sequence-review.json');assert seq['passed'];pins(k,seq['source_pins']);pins(k,seq['input_pins'])
  assert seq['audit_sha256']==sha(root/('audit.json' if root==emu else 'physical-audit.json'))
 cases[name]=dict(physical_closure_sha256=sha(out/'closure.json'),ordinary_closure_sha256=sha(emu/'closure.json'),
  ordinary_sequence_sha256=sha(emu/'sequence-review.json'),physical_sequence_sha256=sha(out/'sequence-review.json'))
for name in ['emulator-pair-review.json','physical-pair-review.json']:assert read(k/name)['passed']
producer=read(k/'producer-analysis.json');assert producer['passed']
assert producer['source_sha256']==sha(k/'analyze-producers.py');pins(k,producer['input_pins'])
lead=read(k/'transfer-source-leads.json');assert lead['passed'] and not lead['transfer_qualified']
assert lead['source_sha256']==sha(k/'inventory-transfer-leads.py')
preservation=read(k/'transfer-source-preservation.json');assert preservation['passed']
assert preservation['inventory_sha256']==sha(k/'transfer-source-leads.json')
assert preservation['source_sha256']==sha(k/'preserve-transfer-leads.py')
pins(k/'artifacts/transfer-leads211',preservation['source_pins'])
r=dict(passed=True,checked_pins=checked,cases=cases,source_sha256=sha(Path(__file__)),baseline_restored=True,physical_access=False,
 actual_upload_coverage_passed=True,only_definition_difference='XWN_UPLOAD_ACCOUNTING',text_bounds_on_scalar_and_body_clocks_off=True,
 strict_whole_boot_qualified=False,performance_qualified=False,full_storage_qualified=False,release_qualified=False,
 limits='Closed narrow scopes and immutable pins. Additional all159-transition review preserves original parser. Ft49 remains strict failure; no NULL-waste, speed, new-mode or promotion claim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed211 evidence pins PASS:',checked)
