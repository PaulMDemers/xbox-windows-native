"""Check recorded installation and workload evidence without launching a guest."""
import array,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
for name in ['probe','matched']:
    r=load(k/(name+'-review.json'))
    assert r['passed'] and r['checksum_valid']
    assert sha(k/(name+'.c'))==r['source_sha256']
    assert sha(k/'Build.ps1')==r['build_script_sha256']
    assert (k/(name+'.c')).read_text()==(k.parent/'fatx0098-soak'/(name+'.c')).read_text().replace('xwns98','xwns99')
f=load(k/'fixture-001.json')
assert f['software_edit']['only_expected_value_changed'] and f['startup_unchanged']
assert sha(k/'xwnvideo.inf')==next(v['sha256'] for v in f['payloads'] if v['path']=='xwninf99/xwnvideo.inf')
f2=load(k/'fixture-002.json')
assert not f2['installation_run_strict_passed'] and not f2['preceding_dashboard_return']
assert f2['software_unchanged_during_second_staging'] and not f2['startup_unchanged']
assert not f2['video_trace_reset']
def reserved(case):
    raw=(k/case/'artifacts/fat-metadata.bin').read_bytes()
    fat=array.array('I');fat.frombytes(raw[4096:])
    if sys.byteorder!='little':fat.byteswap()
    ids=array.array('I',(i for i,v in enumerate(fat) if v==0xfffffff7))
    if sys.byteorder!='little':ids.byteswap()
    return dict(count=len(ids),positions_sha256=hashlib.sha256(ids.tobytes()).hexdigest())
baseline_allocation=load(k/'before/allocation.json')
assert baseline_allocation['allocation_consistent']
reservation_baseline=reserved('before')
allocation_rows=[]
for case in ['003','004']:
    allocation=load(k/case/'allocation.json');capture=load(k/case/'allocation-capture.json')
    assert capture['read_only'] and not capture['physical_access'] and capture['nbd_process_closed']
    allocation_rows.append(dict(case=case,allocation_consistent=allocation['allocation_consistent'],
        reservations_unchanged=reserved(case)==reservation_baseline,reserved_marks=reserved(case)))
rows=[]
for case in ['001','002','003','004']:
    a=load(k/case/'audit.json');p=load(k/case/'package-audit.json');l=load(k/case/'launch.json')
    assert not a['physical_access'] and not l['physical_access']
    assert len(l['cycles'])==1 and l['host']=='127.0.0.1'
    assert p['combined_checks_passed']==(p['installation_checks_passed'] and a['ordinary_run_valid'])
    assert not p['hardware_qualified']
    assert len(a['hives'])==5 and all(v['parsed'] for v in a['hives'])
    if case=='001':
        assert p['installation_checks_passed'] and not p['combined_checks_passed']
        assert a['probe_completed'] and a['mapping_checks']==527
        assert len(a['popup_records'])==1 and a['normal_shutdown_count']==1
        assert not a['dashboard_return'] and (k/case/'termination.json').exists()
    if case in ['003','004']:
        fixture=load(k/('fixture-'+case+'.json'))
        assert fixture['independent_repeat'] and fixture['fresh_workload_logs_verified_absent']
        assert fixture['fixture_sha256']==f2['fixture_sha256'] and fixture['seed_sha256']==f2['seed_sha256']
        assert a['first_boot_workload_preserved']['passed']
    rows.append(dict(case=case,workload_passed=a['probe_completed'],mapping_checks=a['mapping_checks'],
        persistence_passed=a['persistence_passed'],popups=len(a['popup_records']),
        normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
        installation_checks_passed=p['installation_checks_passed'],combined_checks_passed=p['combined_checks_passed']))
result=dict(scope='Recorded evidence verification, not hardware or general stability qualification',
    passed=True,physical_access=False,cases=rows,allocation=allocation_rows,
    limits="Evidence review acceptance does not promote first-install failure or qualify hardware.")
(k/'evidence-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
