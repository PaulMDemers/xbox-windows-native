"""Independent closed219 pair/input/live-layout evidence review; never launch."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'pair-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked=0;dependencies={}
def pin(path,digest):
 global checked
 assert sha(path)==digest,str(path);checked+=1;dependencies[str(path)]=digest
for path,digest in read(k/'emulator-frozen.json').items():pin(ws/path,digest)
for path,digest in read(k/'observer002-frozen.json').items():pin(ws/path,digest)
for name in ['build-review.json','native-input-review.json','host-tests002.json','source-review.json','patch-review002.json','compiled-reset-review.json']:assert read(k/name)['passed'],name
host=read(k/'host-tests002.json');pin(k/'test-host.py',host['source_sha256']);pin(k/'test-drawing.c',host['harness_sha256']);pin(k/'boot_layout.h',host['layout_sha256'])
patch=read(k/'patch-review002.json');pin(k/'boot-layout219-002.patch',patch['patch_sha256'])
sys.path.insert(0,str(ws/'outputs/video-upload-runtime211'));from upload_sequence import review
for name in ['upload_sequence.py','upload_analysis.py']:dependencies[str(ws/'outputs/video-upload-runtime211'/name)]=sha(ws/'outputs/video-upload-runtime211'/name)
r=dict(passed=False,source_sha256=sha(Path(__file__)),physical_access=False,guest_launch=False,cases={},input_pins=dependencies)
fixtures={};audits={}
for case in ['control001','candidate001']:
 out=k/('emu-'+case);a=read(out/'audit.json');c=read(out/'closure.json');state=read(out/'host-state.json');launch=read(out/'launch.json');f=read(k/('fixture-'+case+'.json'));fixtures[case]=f;audits[case]=a
 assert c['closed'] and c['audit_sha256']==sha(out/'audit.json') and state['closed'] and state['status']=='cold_audited_closed'
 assert state['source_sha256']==sha(k/'run-emulator.py') and state['runner_exit_code']==state['observer_exit_code']==state['audit_exit_code']==0
 assert len(launch['cycles'])==1 and launch['cycles'][0]['status']=='accepted' and launch['cycles'][0]['dashboard_return']
 assert a['scoped_display_passed'] and a['display_workload_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
 assert not a['strict_qualification_passed'] and not a['ordinary_qualified'] and len(a['warnings_errors'])==1
 event=a['warnings_errors'][0];assert event['source']=='Ftdisk' and event['event_id']==49 and event['strings']==['\\Device\\HarddiskVolume6']
 assert not a['new_events']['application'] and not a['measurement_events']
 assert f['inherited_null_policy'] is False
 allocation=read(out/'allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
 assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives']) and len(a['files'])==28 and all(v['matched'] for v in a['files'])
 samples=[]
 for i in range(5):
  path=out/'artifacts'/('sample%d/gdi-baseline.txt'%i);dependencies[str(path)]=sha(path);v=review(path.read_bytes().decode('ascii'),1);assert v['passed'] and v['all_159_snapshot_transitions_monotonic'];samples.append(v)
 run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/blayout219-runs/nt5-blayout219-'+case)
 assert c['cleanup_sha256']==sha(run/'cleanup.json') and state['instance_sha256']==sha(run/'instance.json')
 r['cases'][case]=dict(scoped_display_passed=True,strict_qualification_passed=False,sole_error=event,allocation={n:allocation[n] for n in ['directories','files','directory_clusters','orphan_cluster_count']},protected_files=28,hives=5,normal_shutdown_count=1,dashboard_return=True,audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),cold_disk_sha256=sha(run/'hdd.qcow2'),sequence_samples=samples)
# Existing payloads/policy are equal; only the paired boot provider and fresh namespace differ.
left,right=[fixtures[n] for n in ['control001','candidate001']]
assert left['parent_sha256']==right['parent_sha256'] and left['device_policy']==right['device_policy']
for name,digest in left['protected'].items():
 if name=='E/Applications/XWNFBoot/loader/xboxbvid.dll':continue
 if name.startswith('F/'+left['namespace']+'/'):name='F/'+right['namespace']+'/'+name.split('/',2)[2]
 assert right['protected'][name]==digest,name
assert audits['control001']['actual_caps']==audits['candidate001']['actual_caps'] and audits['control001']['actual_modes']==audits['candidate001']['actual_modes']
old=read(k/'emu-control001/live-layout.json');assert old['closed'] and not old['passed'] and not old['cpu_stopped']
live=read(k/'emu-candidate001/live-layout002.json');pin(k/'observe-layout002.py',live['source_sha256'])
assert live['closed'] and live['passed'] and live['complete'] and not live['cpu_stopped'] and not live['debugger_memory_mutated']
assert live['hidden_offset']==0x39dd00 and live['cells']['_BootWritableBytes']==0x3eb000 and live['resident_reset_pin']['matched_relocated_disk']
gates=live['kernel_discovery']['gates'];assert len(gates)==2 and gates[0]['base']==gates[1]['base']==live['kernel_discovery']['kernel_base']
pages=read(k/'emu-candidate001/live-pages003.json');pin(k/'observe-pages003.py',pages['source_sha256']);assert pages['layout_observation_sha256']==sha(k/'emu-candidate001/live-layout002.json')
assert pages['passed'] and pages['closed'] and not pages['cpu_stopped'] and not pages['guest_memory_mutated'] and pages['pages']==1024
next_page=0
for group in pages['groups']:
 assert group['first_page']==next_page and group['second_read_equal'] and group['pages']==len(group['ptes'])
 for j,pte in enumerate(group['ptes']):assert pte&1 and pte&16 and (pte&0xfffff000)==0x03c00000+(next_page+j)*4096
 next_page+=group['pages']
assert next_page==1024 and pages['hidden_physical']==0x03f9dd00 and pages['protected_start']==0x03feb000
for case in ['control001','candidate001']:
 out=k/('emu-'+case)
 for path in out.glob('*.json'):dependencies[str(path)]=sha(path)
r.update(passed=True,verified_pins=checked,actual_caps=audits['candidate001']['actual_caps'],actual_modes=audits['candidate001']['actual_modes'],candidate_live_layout_passed=True,candidate_mapping_pages=1024,original_observer_failed_preserved=True,matched_original_payloads_and_policy=True,strict_overall_qualified=False,runtime_tail_guard_qualified=False,crash_rendering_qualified=False,gpu_transfer_qualified=False,physical_qualified=False,performance_qualified=False,release_qualified=False,limits='Matched ordinary display/cold scope and read-only live layout/page bits only. Ft49 is a strict failure; actual tail guards/reset/crash rendering remain pending. Allocation/hive/protected checks are not exhaustive file-content safety.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed pair, five full sequences each, and read-only layout/pages review PASS:',checked)
