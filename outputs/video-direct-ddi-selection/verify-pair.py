"""Qualify the two closed direct-DDI runs without relaxing existing gates."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'pair-review.json';assert not dest.exists();r=dict(passed=False,physical_access=False,debugger=False,results=[],source_sha256=sha(Path(__file__)))
fixtures=[]
for kit,case in [(k.parent/'video-direct-ddi','control001'),(k,'candidate001')]:
 out=kit/case;a=read(out/'audit.json');f=read(kit/('fixture-'+case+'.json'));fixtures.append(f)
 assert (out/'closure.json').exists()
 for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
 config=read(out/'after-configuration.json')
 before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json')
 pagefile=all(before[n]==after[n] for n in ['file_size','clusters','first_cluster','requested_65536','whole_file'])
 trace=(out/'artifacts/video-trace.bin').read_bytes();assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
 count,dropped=struct.unpack_from('<II',trace,16);assert count<=254
 events=[list(struct.unpack_from('<4I',trace,32+i*16)) for i in range(count)]
 shared=[v for v in events if v[0] in [0x30,0x31,0x32]];acq=[v for v in shared if v[0]==0x30]
 observed=bool(acq) and all(v[1]==0 and v[2]>=0x80000000 and not v[2]%4096 and v[3]==0x3c00000 for v in acq) and all(v[1]==0 for v in shared)
 strict=not (out/'timeout-memory.json').exists() and a['strict_qualification_passed'] and config['expected_configuration'] and pagefile and observed and dropped==0
 allocation=read(out/'allocation.json')
 r['results'].append(dict(case=case,strict=bool(strict),identity_and_pixels=a['protocol_exact'],
  cases=len(a['protocol_details'].get('cases',[])),pixel_stages=a['protocol_details'].get('verified_pixel_stages'),
  normal_shutdown=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],
  config_passed=config['expected_configuration'],display_selection=config['display_selection'],pagefile_unchanged=pagefile,
  shared_events=shared,shared_contract_observed=bool(observed),trace_records=count,trace_dropped=dropped,
  allocation_passed=a['allocation_passed'],warnings_errors=a['warnings_errors'],
  pins={n:sha(out/n) for n in ['audit.json','closure.json','preflight.json','allocation.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json','artifacts/video-trace.bin']}))
a,b=fixtures
assert a['parents']==b['parents'] and a['protected']==b['protected'] and a['startup_sha256']==b['startup_sha256']
ap={p['path']:p['sha256'] for p in a['payloads']};bp={p['path']:p['sha256'] for p in b['payloads']}
assert set(ap)==set(bp) and [n for n in ap if ap[n]!=bp[n]]==['xwnddi113/expected.bin']
ah={p['path']:p['sha256'] for p in a['preserved_hives']};bh={p['path']:p['sha256'] for p in b['preserved_hives']}
assert [n for n in ah if ah[n]!=bh[n]]==['winnt/system32/config/system']
for kit,case in [(k.parent/'video-direct-ddi','control001'),(k,'candidate001')]:assert read(kit/case/'registry-selection.json')['all_other_logical_nodes_values_unchanged']
assert len(read(k/'candidate001/registry-selection.json')['changed_values'])==2
assert read(k/'candidate001/after-configuration.json')['display_selection']==['xwndir','xwndir']
inv=read(k.parent/'video-direct-ddi/selection-inventory.json')
for hive in inv['hives']:
 if hive['case']!='control001':continue
 rows=[v for v in hive['selectors'] if v['path'].casefold() in [r'\controlset001\services\xboxvnt5\device0',r'\controlset001\control\class\{4d36e968-e325-11ce-bfc1-08002be10318}\0001\settings']]
 assert len(rows)==2 and all(v['value']=='framebuf' for v in rows)
r.update(passed=all(row['strict'] for row in r['results']),
 changed_inputs=['Expected-driver one-byte marker','Two bound display InstalledDisplayDrivers values in candidate SYSTEM hive'],
 limits='One ordinary boot per driver at1024x576x32, identity escape and54/162 drawing checks. No shadow/GPU/cache change, exhaustive DDI/scanout/crash/PnP or physical performance qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
