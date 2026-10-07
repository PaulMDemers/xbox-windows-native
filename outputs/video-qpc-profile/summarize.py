"""Compare only complete ordinary QPC instrumentation cases with identical drivers."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
fixtures=[];measurements=[];evidence={}
for case,detail in [('control001',0),('instrumented001',1)]:
 out=k/case;a=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'));c=read(out/'closure.json');pre=read(out/'preflight.json')
 assert a['strict_qualification_passed'] and not a['debugger'] and not a['explicit_ui_intervention']
 assert a['protocol_details']['cursor_configuration']==f['cursor_configuration']==[820,460,1]
 assert a['protocol_details']['qpc_mode']==f['qpc_mode']==detail
 for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
 for row in f['parents']:assert sha(host(row['path']))==row['sha256']
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
 assert sha(Path(c['private_disk']))==c['private_disk_sha256']
 for n,h in c['run_metadata_sha256'].items():assert sha(Path(c['private_disk']).parent/n)==h
 before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
 assert before['clusters']==after['clusters'] and before['whole_file']==after['whole_file']
 assert all(read(out/(phase+'-configuration.json'))['expected_configuration'] for phase in ['before','after'])
 assert len(a['protocol_details']['cases'])==54 and a['protocol_details']['verified_pixel_stages']==162
 assert all(v['elapsed_ms']>=300 or v['count']==4096 for v in a['protocol_details']['cases'])
 vals={}
 for w,h in [(64,64),(256,128),(768,384)]:
  for kind in range(6):
   samples=[v for v in a['protocol_details']['cases'] if v['width']==w and v['height']==h and v['kind']==kind];assert len(samples)==3
   freq=a['protocol_details']['qpc_frequency']
   times=[v['qpc_outer']*1000/(freq*v['count']) for v in samples]
   components={name:statistics.median(v['qpc_'+name]*1000/(freq*v['count']) for v in samples) for name in ['operation','flush','checks','unbracketed']}
   calibration=[c['sum_ticks']*1000/(freq*c['count']) for v in samples for c in v['calibration']]
   vals[(w,h,kind)]=dict(median=statistics.median(times),minimum=min(times),maximum=max(times),components_median_ms=components,calibration_mean_ms_range=[min(calibration),max(calibration)],samples=samples)
 fixtures.append(f);measurements.append(vals);evidence[case]={n:sha(out/n) for n in ['preflight.json','audit.json','closure.json','before-configuration.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json']}
for n in ['parents','protected','preserved_hives','payloads','build_review_sha256','parent_manifest_sha256','cursor_configuration']:assert fixtures[0][n]==fixtures[1][n]
assert fixtures[0]['startup_sha256']!=fixtures[1]['startup_sha256']
names=['fill','upload','readback','screen_overlap','memory_overlap_upload','memory_overlap'];rows=[]
for key,control in measurements[0].items():
 w,h,kind=key;instrumented=measurements[1][key]
 rows.append(dict(width=w,height=h,path=names[kind],control=control,instrumented=instrumented,instrumented_over_control=instrumented['median']/control['median']))
r=dict(passed=True,physical_access=False,debugger=False,drivers_changed=False,matched_probe_sha256=fixtures[0]['payloads'][0]['sha256'],timings=rows,evidence=evidence,source_sha256=sha(Path(__file__)),limits='Raw guest QPC times with adjacent-pair calibration, stable frequency and coarse-clock agreement. Components include query boundary cost; no guessed subtraction. Control checks instrumentation perturbation. Shared functional emulator slot, one run per mode and three rotated rounds; not physical throughput or FPS. Fixed visible arrow outside copied regions in both runs. All preparation before measurements.')
p=k/'pair-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=True,large=[dict(path=v['path'],control_ms=v['control']['median'],instrumented_ms=v['instrumented']['median'],ratio=v['instrumented_over_control'],components=v['instrumented']['components_median_ms'],calibration_ms=v['instrumented']['calibration_mean_ms_range']) for v in rows if v['width']==768]),indent=2))
