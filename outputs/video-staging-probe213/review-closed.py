"""Read-only212/213 closed evidence verification; never launch or collect a guest."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];contracts=k.parent/'video-gpu-transfer-contract212'
dest=k/'evidence-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked=0
def pin(p,digest):
 global checked
 assert sha(p)==digest,str(p);checked+=1
for name,digest in read(k/'emulator-frozen.json').items():pin(ws/name,digest)
repair=read(k/'audit-repair001.json');pin(k/'boundary_analysis.py',repair['dependency_sha256'])
pin(k.parent/'video-upload-runtime211/boundary_analysis.py',repair['matched_211_sha256'])
pin(k/'audit-emulator.py',repair['original_audit_sha256']);pin(k/'emulator-frozen.json',repair['original_frozen_sha256'])
expected=(k/'audit-emulator.py').read_text().replace('case=sys.argv[1];',"assert sha(k/'boundary_analysis.py')==read(k/'audit-repair001.json')['dependency_sha256']\ncase=sys.argv[1];",1)
assert (k/'audit-emulator002.py').read_text()==expected
for filename in ['native-input-review.json','build-review.json','host-tests003.json','parser-tests.json','emulator-pair-review.json']:
 assert read(k/filename)['passed'],filename
assert read(k/'native-input-review.json')['build_sha256']==sha(k/'build003.json')
pin(k/'review-native-inputs.py',read(k/'native-input-review.json')['source_sha256'])
for filename,script in [('binary-inventory.json','inventory-binaries.py'),('source-inventory002.json','inventory-source002.py'),
 ('abi-review.json','review-abi.py'),('boot-reservation.json','inventory-boot-reservation002.py'),('ramin-model.json','inventory-ramin-model003.py')]:
 r=read(contracts/filename);assert r['passed'];pin(contracts/script,r['source_sha256'])
r=read(contracts/'source-inventory002.json')
for name,row in r['files'].items():pin(contracts/'artifacts/nt5-source002'/name,row['sha256'])
r=read(contracts/'binary-inventory.json')
for row in r['modules'].values():pin(Path(row['path']),row['sha256'])
for name,digest in r['nxdk_sources'].items():pin(contracts/'artifacts/nxdk'/name,digest)
for name,digest in read(contracts/'boot-reservation.json')['source_pins'].items():pin(contracts/'artifacts/boot-reservation'/name,digest)
pin(contracts/'artifacts/ramin-model003/nv2a.c',read(contracts/'ramin-model.json')['nv2a_sha256'])
cases={}
for name in ['control001','candidate001']:
 out=k/('emu-'+name);host=read(out/'host-state.json');c=read(out/'closure.json');a=read(out/'audit.json');launch=read(out/'launch.json')
 assert host['closed'] and c['closed'] and a['scoped_display_passed'] and a['integrity_passed']
 pin(out/'audit.json',c['audit_sha256'])
 run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/staging213-runs/nt5-staging213-'+name)
 pin(run/'cleanup.json',c['cleanup_sha256']);pin(run/'instance.json',host['instance_sha256'])
 assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return']
 assert launch['cycles'][0]['status']=='accepted'
 assert a['staging_probe']['passed'] and not a['staging_probe']['missed']
 assert a['normal_shutdown_count']==1 and not a['new_events']['application']
 assert not a['strict_qualification_passed'] and not a['gpu_transfer_qualified']
 assert [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
 if name=='control001':
  assert host['status']=='preserved_failure' and host['audit_exit_code']==1
  assert 'ModuleNotFoundError' in (out/'cold-audit-console.txt').read_text()
 else:assert host['status']=='cold_audited_closed' and host['audit_exit_code']==0
 for refusal in host['resource_attempts']:
  assert refusal['resource_busy'] and not refusal['runner_start_exists'] and not refusal['run_exists']
  pin(out/('resource-attempt%d-console.txt'%refusal['attempt']),refusal['log_sha256'])
 # Exact private before/after hive and protected-file identities used by cold gates.
 for row in a['hives']:pin(out/'artifacts'/('after-'+row['name']),row['sha256'])
 pin(out/'artifacts/after-xwn-video-trace.bin',a['staging_probe']['sha256'])
 cases[name]=dict(host_status=host['status'],audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),
  supplemental_audit=name=='control001',strict_qualification_passed=False)
r=dict(passed=True,source_sha256=sha(Path(__file__)),checked_pins=checked,cases=cases,
 frozen_inputs_unchanged=True,missing_dependency_repair_explicit=True,physical_access=False,
 gpu_transfer_qualified=False,performance_qualified=False,strict_qualification_passed=False,
 limits='Preserved host control failure plus one successful supplemental cold audit; no guest repeated. Exact matched native CPU staging scope only. All strict gates retained; no GPU/physical/release promotion.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Closed212/213 evidence pins PASS:',checked)
