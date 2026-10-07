"""Verify raw closed-run evidence without changing any qualification gate."""
import sys
from common import *
case=sys.argv[1];assert case in ['trace001'];out=k/case;pre=read(out/'preflight.json')
for name,digest in pre['sources'].items():assert sha(out/'source'/name)==digest,(case,name)
f=read(k/('fixture-'+case+'.json'));run=ws/('work/runs/nt5-dump-map-trace-'+case)
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
closed=read(out/'closure.json');assert sha(run/'hdd.qcow2')==closed['private_disk_sha256']
for name,digest in closed['run_metadata_sha256'].items():assert sha(run/name)==digest
a=read(out/'audit.json');art=out/'artifacts';log=(art/'result.log').read_bytes()
assert a['log']==log.decode('ascii',errors='backslashreplace')
assert a['protocol_details']==validate_log(f['mode'],log)
for i,row in enumerate(a['files']):
    p=art/f'case{i:02d}.bin';assert p.exists()==row['present']
    if row['present']:
        data=p.read_bytes();assert len(data)==row['size'] and m.sha(data)==row['sha256']
        assert row['matched']==(data==expected(i)) and row['expected_sha256']==m.sha(expected(i))
    else:assert not row['matched']
assert sha(out/'allocation.json')==a['allocation_sha256']
for row in a['hives']:assert sha(art/('after-'+row['name']))==row['sha256']
for phase in ['before','after']:
    c=read(out/(phase+'-configuration.json'));assert sha(art/(phase+'-configuration-system'))==c['system_sha256']
assert a['strict_qualification_passed']==(a['workload_and_persistence_passed'] and a['integrity_passed'] and a['strict_events_passed'])
print(case+' evidence consistent; bounded workload='+str(a['workload_and_persistence_passed'])+'; strict='+str(a['strict_qualification_passed']))
