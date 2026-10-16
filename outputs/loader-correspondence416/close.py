"""Verify prepared candidate evidence; no activation, launch or prior-result rewrite."""
import datetime
import hashlib
import json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=read(K/'comparison002.json');stage=read(K/'stage001.json')
assert q['passed'] and q['all_nonmetadata_bytes_exact'] and q['negative_checks']==77
assert stage['completed'] and stage['inactive'] and stage['protected_after_exact']
assert not stage['launch_requested'] and not stage['active_files_changed']
assert not (K/'activation001.json').exists()
assert read(K/'restore-tests001.json')['states']==256
private={}
for row in q['files']:
    for phase,field in [('candidate','candidate_sha256'),('baseline','baseline_sha256')]:
        p=Path('/mnt/e/xwn416')/phase/row['relative']
        assert sha(p)==row[field];private[str(p)]=sha(p)
    p=Path(row['source_path']);assert sha(p)==row['candidate_sha256'];private[str(p)]=sha(p)
r1=read(K/'build001.json');r2=read(K/'build002.json')
for label,out in [('hal001',r1['cases']['hal']['output']),('loader001',r1['cases']['loader']['output']),('loader002',r2['output'])]:
    p=Path(out)/'build.log';assert sha(p)==q['warnings'][label]['log_sha256'];private[str(p)]=sha(p)
    for name in ['source.json','build.json','build-command.json']:
        assert (Path(out)/name).read_bytes()==(K/label/name).read_bytes()
headers=[Path('/home/paul/xbox-windows-native/build/stock-boot334-build001/nt5/sdk/include/reactos/buildno.h'),
         Path(r1['cases']['loader']['output'])/'build/sdk/include/reactos/buildno.h',
         Path(r2['output'])/'build/sdk/include/reactos/buildno.h']
for i,p in enumerate(headers):
    data=p.read_bytes();dest=Path('/mnt/e/xwn416')/('header'+str(i)+'.h')
    assert not dest.exists();dest.write_bytes(data);private[str(dest)]=sha(dest)
assert sha(headers[0])==sha(headers[2])==r2['original_generated_header_sha256']
for path,h in r1['inputs'].items():assert sha(W/path)==h
for path,h in q['source_inputs'].items():assert sha(W/path)==h
assert sha(K/'stage.py')==stage['source_sha256']
records={str(p.relative_to(W)):sha(p) for p in K.rglob('*') if p.is_file()}
for name in ['src/boot/xromwell/boot/BootResetAction.c','src/boot/loader/boot/freeldr/freeldr/freeldr.c',
             'src/boot/loader/boot/freeldr/freeldr/ntldr/winldr.c',
             'outputs/media-physical407/physical.py','outputs/demo-audio-level256/common001.py',
             'outputs/surface-bridge260/atomic_json.py','docs/building.md']:
    records[name]=sha(W/name)
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),prepared=True,
            all_nonmetadata_bytes_exact=True,mutation_checks=77,rollback_planner_states=256,
            candidate_staged_inactive=True,physical_active_demo_unchanged=True,
            physical_C_accessed=False,guest_launches=0,actual_candidate_boot_qualified=False,
            original_partial_comparison_retained=True,public_release_ready=False,
            new_warning_messages=[],owned_subprocesses_closed=True,
            private_files=private,records_sha256=records,
            pending='User screen observation/readiness for same File Explorer launch; no activation requested')
with (K/'final-review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(prepared=True,records=len(records),private_files=len(private),active_demo_unchanged=True)))
