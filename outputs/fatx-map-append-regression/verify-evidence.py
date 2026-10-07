"""Verify closed evidence and exact source/raw-byte pins, not convert a FAIL into PASS."""
import sys
from common import *
case=sys.argv[1];assert case in ['mode0','mode0b','settled0','settled1']
out=k/case;pre=read(out/'preflight.json')
for name,digest in pre['sources'].items():
    path=out/'source'/name
    if not path.exists():path=k/name
    assert sha(path)==digest,(case,name)
f=read(k/('fixture-'+case+'.json'))
assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
run=ws/('work/runs/nt5-fatx-map-append-'+case)
assert (run/'cleanup.json').exists()
closed=read(out/'closure.json');assert sha(run/'hdd.qcow2')==closed['private_disk_sha256']
for name,digest in closed['run_metadata_sha256'].items():assert sha(run/name)==digest
if case=='mode0':
    assert read(out/'host-failure.json')['windows_launch_requested'] is False
    assert not (out/'launch.json').exists()
    print('mode0 host failure preserved; no guest result');sys.exit(0)
a=read(out/'audit.json');art=out/'artifacts'
assert a['log']==(art/'result.log').read_bytes().decode('ascii',errors='backslashreplace')
assert a['protocol_exact']==((art/'result.log').read_bytes()==protocol(f['mode']))
for i,row in enumerate(a['files']):
    path=art/f'case{i:02d}.bin';assert path.exists()==row['present']
    if row['present']:
        data=path.read_bytes();assert len(data)==row['size'] and m.sha(data)==row['sha256']
        assert row['matched']==(data==expected(i)) and row['expected_sha256']==m.sha(expected(i))
    else:assert not row['matched']
assert sha(out/'allocation.json')==a['allocation_sha256']
for row in a['hives']:assert sha(art/('after-'+row['name']))==row['sha256']
if case=='mode0b':
    assert a['log']=='ATTEMPT_ONCE 0 13 4\r\nINSTALL_IDLE_START 258 0 0\r\n'
    assert not any(row['present'] for row in a['files']) and not a['workload_and_persistence_passed']
    assert not a['normal_shutdown_count'] and not a['strict_qualification_passed']
else:
    for phase in ['before','after']:
        c=read(out/(phase+'-configuration.json'))
        assert c['expected_configuration'] and sha(art/(phase+'-configuration-system'))==c['system_sha256']
assert a['strict_qualification_passed']==(a['workload_and_persistence_passed'] and a['integrity_passed'] and a['strict_events_passed'])
print(case+' evidence consistent; strict qualification='+str(a['strict_qualification_passed']))
