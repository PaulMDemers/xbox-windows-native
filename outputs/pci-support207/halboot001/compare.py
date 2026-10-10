"""Compare two closed native HAL boots without claiming terminal or bus qualification."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(k/'build001.json');follow=read(k/'attempt002-inputs.json')
assert sha(k/'build001.json')==follow['build_manifest_sha256']
for v in build['sources']:assert sha(k/v['name'])==v['sha256'],v['name']
for v in build['files']:assert sha(k/'artifacts/build001'/v['name'])==v['sha256'],v['name']
for name,digest in follow['sources'].items():assert sha(k/name)==digest,name
assert read(k/'build-review001.json')['passed'] and read(k/'e-tests001.json')['passed']
fixtures=[read(k/(v+'002')/'fixture.json') for v in ('control','candidate')]
assert fixtures[0]['base_sha256']==fixtures[1]['base_sha256']
changes=[name for name in fixtures[0]['files'] if fixtures[0]['files'][name]!=fixtures[1]['files'][name]]
assert set(fixtures[0]['files'])==set(fixtures[1]['files'])
assert set(changes)=={'E/Applications/XWNFBoot/loader/halxboxnt5.dll','F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'}
hal=read(k.parent/'handoff001/build001.json');assert sha(k.parent/'handoff001/build001.json')==fixtures[0]['hal_build_record_sha256']==fixtures[1]['hal_build_record_sha256']
result=dict(scope=__doc__,passed=True,physical_access=False,source_pins_match=True,prepared_file_differences=changes,trials=[])
for variant,fixture in zip(('control','candidate'),fixtures):
    out=k/(variant+'002');a=read(out/'audit.json');p=read(out/'pnp-review.json');r=read(out/'run.json')
    assert r['closed'] and r['source_unchanged'] and a['integrity_passed'] and a['e_allocation']['allocation_consistent'] and a['e_allocation_metadata_unchanged']
    assert p['qualified_resource_only_installation'] and p['hal_probe_passed'] and p['lifecycle_completed']
    lines=p['log'].splitlines();expected=int(variant=='candidate')
    assert lines.count('hal_probe_ok=1')==4 and lines.count('hal_export='+str(expected))==4
    assert lines.count('hal_invalid_ntstatus=0')==4 and lines.count('hal_invalid_result='+str(expected))==4
    assert lines.count('hal_invalid_status=0')==4 and lines.count('hal_invalid_polls=0')==4 and lines.count('hal_invalid_data=0')==4
    assert lines.count('power_status=0')==6 and lines.count('power_gate=0')==3 and lines.count('power_gate=1')==3
    assert 'remove_result=0' in lines and 'REMOVE_INTERFACE_ABSENT' in lines and 'reenumerate_result=0' in lines
    trace=read(out/'resource-trace.json');minors=[v['profile'] for v in trace['records'] if v['stage']==5]
    assert minors.count(1)==2 and minors.count(2)==2 and minors.count(0)==3
    result['trials'].append(dict(variant=variant,hal_sha256=fixture['hal_sha256'],launched=r['launch_requested_utc'],closed=r['closed_utc'],integrity_passed=True,e_allocation=a['e_allocation'],hal_export_expected=expected,hal_probe_passes=4,lifecycle_completed=True,power_transition_count=6,pnp_minors=minors,pending_setup_hold=p['restart_held_pending_setup'],normal_restart_qualified=p['normal_restart_qualified'],normal_shutdown_events=a['normal_shutdown_event_count'],dashboard_return=r.get('dashboard_return_utc'),warnings_errors=a['warnings_errors'],run_sha256=sha(out/'run.json'),audit_sha256=sha(out/'audit.json'),pnp_review_sha256=sha(out/'pnp-review.json'),do_not_relaunch=True))
result['limits']='Native emulator boot, invalid-only ABI and resource lifecycle pass. No functional SMBus transaction, terminal takeover execution, stuck-bus runtime injection, ordinary cold-boot persistence, STOP/cancel or physical qualification.'
result['python_syntax_checked']=0
for path in k.glob('*.py'):ast.parse(path.read_text(),filename=str(path));result['python_syntax_checked']+=1
dest=k/'comparison001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(passed=result['passed'],trials=[{a:t[a] for a in ('variant','integrity_passed','hal_probe_passes','lifecycle_completed','pending_setup_hold','normal_restart_qualified')} for t in result['trials']]),indent=2))
