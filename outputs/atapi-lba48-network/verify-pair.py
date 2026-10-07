"""Verify the closed ordinary ATAPI comparison and unchanged dump configuration."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=['control001','candidate001'];fixtures=[read(k/('fixture-'+c+'.json')) for c in cases];audits=[read(k/c/'audit.json') for c in cases]
settings=[];maps=[]
for case,f,a in zip(cases,fixtures,audits):
    assert (k/case/'closure.json').exists() and not a['debugger'] and not a['explicit_ui_intervention']
    assert f['mode']==0 and f['readback_verified'] and f['result_absent']
    assert a['strict_qualification_passed']==(a['network_passed'] and a['workload_and_persistence_passed'] and a['integrity_passed'] and a['strict_events_passed'])
    for n,d in read(k/case/'preflight.json')['sources'].items():assert sha(k/case/'source'/n)==d
    for phase in ['before','after']:
        path=k/case/'artifacts'/(phase+'-configuration-system');h=hivex.Hivex(str(path))
        assert sha(path)==read(k/case/(phase+'-configuration.json'))['system_sha256']
        def node(p):
            n=h.root()
            for part in p.split('\\'):n=h.node_get_child(n,part);assert n
            return n
        def value(p,name):
            v=h.node_get_value(node(p),name);assert v;typ,data=h.value_value(v)
            return dict(type=typ,data_hex=data.hex())
        cs='ControlSet%03d'%int.from_bytes(bytes.fromhex(value('Select','Current')['data_hex']),'little')
        cc=cs+r'\Control\CrashControl';mm=cs+r'\Control\Session Manager\Memory Management'
        record={n:value(cc,n) for n in ['CrashDumpEnabled','LogEvent','AutoReboot','Overwrite','DumpFile']}
        record['PagingFiles']=value(mm,'PagingFiles');settings.append(record)
        assert int.from_bytes(bytes.fromhex(record['CrashDumpEnabled']['data_hex']),'little')==3
        pm=read(k/case/(phase+'-pagefile-map.json'));maps.append({n:pm[n] for n in ['file_size','clusters','cluster_size','partition_offset','partition_size','requested_65536','whole_file']})
assert all(v==settings[0] for v in settings) and all(v==maps[0] for v in maps)
for key in ['parents','preserved_hives','payloads','startup_sha256','parent_manifest_sha256','build_review_sha256','hal_after_sha256']:
    assert fixtures[0][key]==fixtures[1][key],key
diff=[]
for before,after in zip(fixtures[0]['protected'],fixtures[1]['protected']):
    assert (before['volume'],before['path'])==(after['volume'],after['path'])
    if before['sha256']!=after['sha256']:diff.append(before['volume']+'/'+before['path'])
assert diff==['F/winnt/system32/drivers/atapi.sys']
assert read(k/'inputs.json')['profiles']==read(k/'control-inputs.json')['profiles']
assert all(a['network_passed'] for a in audits)
r=dict(scope=__doc__,changed_protected_files=diff,same_helper_and_initial_hives=True,same_build_flags=True,same_dump_settings=True,dump_settings=settings[0],same_pagefile_chain=True,pagefile_size=maps[0]['file_size'],expected_65536_mapping=maps[0]['requested_65536'],physical_access=False,actual_crash_dump_write_qualified=False,
    results=[dict(case=case,workload=a['workload_and_persistence_passed'],integrity=a['integrity_passed'],strict=a['strict_qualification_passed'],normal_shutdown_count=a['normal_shutdown_count'],events=[dict(source=e['source'],id=e['event_id'],data=e['data_hex']) for e in a['warnings_errors']]) for case,a in zip(cases,audits)])
target=k/'pair-review.json'
if target.exists():assert read(target)==r
else:target.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
