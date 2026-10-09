"""Independent read-only comparison of two closed ordinary configuration boots."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];first=k.parent/'device-unused-package179';failed=k.parent/'device-settled-reboot180'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'sequence-review.json';assert not dest.exists()
cases=[]
for kit in [first,k]:
 c=kit/'candidate001';a=read(c/'audit.json');p=read(c/'package-verification.json');cl=read(c/'closure.json');assert cl['closed'] and p['configuration_observed']
 pins=read(kit/'frozen-inputs.json')
 for n,d in pins.items():assert sha(ws/n)==d,n
 for source in (c/'source').iterdir():assert source.read_bytes()==(kit/source.name).read_bytes()
 assert a['runner_normal_restart'] and a['normal_shutdown_count']==1 and a['dashboard_return'] and a['integrity_passed']
 assert not a['strict_qualification_passed'] and len(a['warnings_errors'])==1
 e=a['warnings_errors'][0];assert e['source']=='Ftdisk' and e['event_id']==49 and e['type']==1 and e['strings']==['\\Device\\HarddiskVolume6'] and e['data_hex']=='000000000100560000000000310004c0030000000000000000000000000000000000000000000000'
 assert not a['new_events']['application'] and not any(v['source']=='Application Popup' for v in a['new_events']['system'])
 allocation=read(c/'allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
 cases.append(dict(kit=kit.name,launch=read(c/'launch.json'),audit_sha256=sha(c/'audit.json'),package_sha256=sha(c/'package-verification.json'),closure_sha256=sha(c/'closure.json'),
  guard=a['guard_lines'],normal_lifecycle=True,full_integrity=True,allocation=allocation['summary'] if 'summary' in allocation else {n:allocation[n] for n in ['directories','files','directory_clusters']},
  frozen_pins_checked=len(pins),strict_qualified=False,inherited_exact_ftdisk49=True,no_new_popup_or_application_delta=True))
f=read(first/'candidate001/package-verification.json');s=read(k/'candidate001/package-verification.json')
fields=['path','description','driver','service','config_flags','class_guid','inf_path','inf_section','inf_sha256','exact_inf']
bindings=lambda p:[{key:row[key] for key in fields} for row in p['devices']]
assert bindings(f)==bindings(s)
log_first=(first/'candidate001/artifacts/after-setupapi.log').read_bytes();log_before=(k/'candidate001/artifacts/before-setupapi.log').read_bytes();log_after=(k/'candidate001/artifacts/after-setupapi.log').read_bytes()
assert log_first==log_before and log_after.startswith(log_before)
assert read(failed/'candidate001/host-closure.json')['closed'] and not read(failed/'candidate001/host-closure.json')['windows_launch_requested']
assert read(k/'backing-portability.json')['passed'] and read(k/'parent-copy.json')['virtual_disk_equal']
for kit in [first,failed,k]:
 for source in kit.glob('*.py'):ast.parse(source.read_text())
r=dict(review_passed=True,physical_access=False,debugger=False,cases=cases,identical_retained_bindings=bindings(s),no_setup_log_reset=True,
 subsequent_setupapi_unchanged=log_after==log_before,subsequent_setupapi_delta_bytes=len(log_after)-len(log_before),durable_configuration_observed=True,
 failed_host_attempt_preserved=True,backing_portability_verified=True,function_support_qualified=False,strict_release_qualified=False,physical_qualified=False,performance_qualified=False,
 limits='Two observed guarded ordinary lifecycles in explicitly unused-device emulator configuration; audio/SMBus/test function unsupported. No Windows synchronization fix, popup frequency estimate, physical promotion, Ftdisk49 waiver or graphics speedup claim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['review_passed','durable_configuration_observed','subsequent_setupapi_unchanged','strict_release_qualified']}))
