"""Verify frozen launch/captured bytes and closed physical218 evidence without FTP."""
import ast,hashlib,json,datetime
from pathlib import Path

k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'physical-review001.json'
assert not dest.exists()
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=0
for f in list(k.glob('emulator-frozen*.json'))+list(k.glob('build-inputs*.json'))+[k/'physical-inputs.json']:
    pins=read(f);pins=pins.get('files',pins)
    for name,digest in pins.items():
        assert sha(Path(name))==digest,(f,name);checks+=1
r=read(k/'physical001.json');a=read(k/'physical-audit001.json');b=read(k/'physical64-analysis.json')
assert r['launch_requested'] and r['readback_verified'] and r['launch_reply']=='200 EXEC command succeeded.'
assert r['collected'] and r['probe_collection_passed'] and r['baseline_unchanged']
assert len(r['before'])==len(r['after'])==23 and len(r['reports'])==5
for phase in ['before','after','reports']:
    for name,row in r[phase].items():
        p=ws/row['path'];assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'];checks+=1
assert all(v['unchanged'] for v in r['after'].values())
assert datetime.datetime.fromisoformat(r['launch_utc'])<datetime.datetime.fromisoformat(r['observed_return_utc'])<datetime.datetime.fromisoformat(r['collected_utc'])
text=r['report'];pages=[]
for line in text.splitlines():
    if line.startswith('PAGE '):
        p=line.split();assert p[2]=='valid=1' and p[3].split('=')[1]==p[4].split('=')[1];pages.append(int(p[1],16))
assert pages==list(range(0x83feb000,0x83ff0000,4096))+list(range(0xfd710000,0xfd715000,4096))
assert 'QUERY end=83ff0000 padding=00010000' in text and 'COMPLETE 1 LOG_OK 1 STOCK_RESTART_REQUEST' in text
assert r['observed_kernel']==['1','0','4034','1']
assert not r['informative_correlation'] and r['independent_comparison']['reverse16_mismatches']==1550
assert a['passed'] and a['closed'] and len(a['hives'])==5
assert b['post_hoc_discovery'] and b['original_gate_unchanged'] and b['actual']['informative64_correlation']
assert b['actual']['mismatched_bytes']==b['actual']['mismatched_words']==0 and b['host_tests']['passed']
for doc in [r,a,b]:assert not doc['physical_qualified'] and not doc['gpu_alias_proven'] and not doc['nt5_ownership_granted']
assert not a['full_allocation_audit_performed'] and not a['full_file_content_audit_performed']
inputs={}
for n in ['physical218.py','audit-physical218.py','analyze-physical64.py','review-physical218.py']:
    ast.parse((k/n).read_text());inputs[n]=sha(k/n)
for n in ['physical001.json','physical-inputs.json','physical-audit001.json','physical64-analysis.json','REPORT.md','NEXT.md','LAYOUT-NEXT.md']:
    inputs[n]=sha(k/n)
out=dict(passed=True,source_capture_hash_checks=checks,python_ast_scripts=4,
    original_two_hypotheses_passed=False,post_hoc_reverse64_correlation_passed=True,
    closed=True,owned_processes_running=False,physical_qualified=False,
    windows_driver_changed=False,gpu_operation_attempted=False,inputs=inputs,
    limits='No new console access or recollection. Scoped physical probe evidence only; no complete allocation/all-file audit or GPU ownership/acceleration qualification.')
dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({n:out[n] for n in ['passed','source_capture_hash_checks','python_ast_scripts','closed']}))
