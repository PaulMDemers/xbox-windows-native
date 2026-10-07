"""Combine closed ordinary evidence without relaxing any event or integrity gate."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'pair-review.json';assert not dest.exists()
r=dict(physical_access=False,debugger=False,results=[],passed=False)
fixtures=[]
for case in ['control001','candidate001']:
    out=k/case;a=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'));fixtures.append(f)
    assert (out/'closure.json').exists()
    frozen=read(out/'preflight.json')
    for n,h in frozen['sources'].items():assert sha(out/'source'/n)==h
    assert sha(k/('fixture-'+case+'.json'))==frozen['sources']['fixture-'+case+'.json']
    config=read(out/'after-configuration.json');before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json')
    pagefile=all(before[n]==after[n] for n in ['file_size','clusters','first_cluster','requested_65536','whole_file'])
    trace=(out/'artifacts/video-trace.bin').read_bytes()
    assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
    count,dropped=struct.unpack_from('<II',trace,16);assert count<=254
    events=[list(struct.unpack_from('<4I',trace,32+i*16)) for i in range(count)]
    shared=[v for v in events if v[0] in [0x30,0x31,0x32]]
    acq=[v for v in shared if v[0]==0x30]
    observed=not shared if case=='control001' else bool(acq) and all(v[1]==0 and v[2]>=0x80000000 and not v[2]%4096 and v[3]==0x3c00000 for v in acq) and all(v[1]==0 for v in shared)
    strict=a['strict_qualification_passed'] and config['expected_configuration'] and pagefile and observed and dropped==0
    r['results'].append(dict(case=case,strict=bool(strict),audit_passed=a['strict_qualification_passed'],config_passed=config['expected_configuration'],pagefile_unchanged=pagefile,trace_records=count,trace_dropped=dropped,shared_events=shared,shared_contract_observed=bool(observed),normal_shutdown=a['normal_shutdown_count'],cases=len(a['protocol_details']['cases']),pixel_stages=a['protocol_details'].get('verified_pixel_stages'),warnings_errors=a['warnings_errors'],pins={n:sha(out/n) for n in ['audit.json','closure.json','preflight.json','allocation.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json','artifacts/video-trace.bin']}))
a,b=fixtures
assert a['parents']==b['parents'] and a['preserved_hives']==b['preserved_hives'] and a['payloads']==b['payloads'] and a['startup_sha256']==b['startup_sha256']
changed=[]
for x,y in zip(a['protected'],b['protected']):
    assert (x['volume'],x['path'])==(y['volume'],y['path'])
    if x['sha256']!=y['sha256']:changed.append([x['volume'],x['path']])
assert changed==[['F','winnt/system32/drivers/xboxvnt5.sys'],['E','Applications/XWNFBoot/loader/xboxbvid.dll']]
r.update(passed=all(v['strict'] for v in r['results']),changed_protected_files=changed,
         limits='Ordinary boot/drawing/normal restart evidence only. Trace records show returned provider pointer, not exhaustive PTE/alias/TLB proof. Crash rendering, generic PnP stop/remove and WC transition remain unqualified. No physical speed claim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
