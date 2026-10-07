"""Audit matched ordinary runs without promoting self-checks to scanout proof."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=k/'pair-review.json';assert not dest.exists()
r=dict(passed=False,physical_access=False,debugger=False,results=[],source_sha256=sha(Path(__file__)))
fixtures=[]
for case in ['control001','candidate001']:
 out=k/case;a=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'));fixtures.append(f)
 closure=read(out/'closure.json')
 assert sha(Path(closure['private_disk']))==closure['private_disk_sha256']
 for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
 config=read(out/'after-configuration.json');before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json')
 pagefile=all(before[n]==after[n] for n in ['file_size','clusters','first_cluster','requested_65536','whole_file'])
 trace=(out/'artifacts/video-trace.bin').read_bytes();assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
 count,dropped=struct.unpack_from('<II',trace,16);assert count<=254
 events=[list(struct.unpack_from('<4I',trace,32+i*16)) for i in range(count)]
 shared=[v for v in events if v[0] in [0x30,0x31,0x32]];acq=[v for v in shared if v[0]==0x30]
 observed=bool(acq) and all(v[1]==0 and v[2]>=0x80000000 and not v[2]%4096 and v[3]==0x3c00000 for v in acq) and all(v[1]==0 for v in shared)
 strict=not a['debugger'] and a['strict_qualification_passed'] and config['expected_configuration'] and pagefile and observed and dropped==0
 r['results'].append(dict(case=case,strict=bool(strict),identity_pixels_selfcheck=a['protocol_exact'],cases=len(a['protocol_details'].get('cases',[])),
  pixel_stages=a['protocol_details'].get('verified_pixel_stages'),callback_counts=a['protocol_details'].get('shadow_callbacks'),
  upload_bytes=a['protocol_details'].get('shadow_bytes'),normal_shutdown=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
  config_passed=config['expected_configuration'],display_selection=config['display_selection'],pagefile_unchanged=pagefile,
  shared_events=shared,shared_contract_observed=bool(observed),trace_records=count,trace_dropped=dropped,
  allocation_passed=a['allocation_passed'],warnings_errors=a['warnings_errors'],
  pins={n:sha(out/n) for n in ['audit.json','closure.json','preflight.json','allocation.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json','artifacts/video-trace.bin']}))
a,b=fixtures
assert a['parents']==b['parents'] and a['protected']==b['protected'] and a['startup_sha256']==b['startup_sha256']
ap={p['path']:p['sha256'] for p in a['payloads']};bp={p['path']:p['sha256'] for p in b['payloads']}
assert set(ap)==set(bp) and [n for n in ap if ap[n]!=bp[n]]==['xwnram114/expected.bin']
ah={p['path']:p['sha256'] for p in a['preserved_hives']};bh={p['path']:p['sha256'] for p in b['preserved_hives']}
assert [n for n in ah if ah[n]!=bh[n]]==['winnt/system32/config/system']
for case,selection in [('control001','xwndir'),('candidate001','xwnram')]:
 s=read(k/case/'registry-selection.json');assert s['all_other_logical_nodes_values_unchanged'] and len(s['changed_values'])==2
 assert all(bytes.fromhex(v['after']).decode('utf-16le').rstrip('\0')==selection for v in s['edits'])
r.update(passed=all(v['strict'] for v in r['results']),
 independent_scanout_qualified=False,physical_qualified=False,
 changed_inputs=['one-byte expected-driver marker','exactly two display selector values'],
 limits='One ordinary boot per driver;54cases162GDI readbacks plus54 candidate driver self-comparisons. Not independent scanout, complete callback, cursor/mode/crash or physical performance qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
