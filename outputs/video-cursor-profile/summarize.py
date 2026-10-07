"""Compare only complete ordinary pointer-position cases with identical drivers."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
fixtures=[];measurements=[];evidence={}
for case,position in [('inside001',[512,288,0]),('outside001',[1000,550,1])]:
 out=k/case;a=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'));c=read(out/'closure.json');pre=read(out/'preflight.json')
 assert a['strict_qualification_passed'] and not a['debugger'] and not a['explicit_ui_intervention']
 assert a['protocol_details']['cursor_configuration']==f['cursor_configuration']==position
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
   times=[v['elapsed_ms']/v['count'] for v in samples];vals[(w,h,kind)]=dict(median=statistics.median(times),minimum=min(times),maximum=max(times),samples=samples)
 fixtures.append(f);measurements.append(vals);evidence[case]={n:sha(out/n) for n in ['preflight.json','audit.json','closure.json','before-configuration.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json']}
for n in ['parents','protected','preserved_hives','payloads','build_review_sha256','parent_manifest_sha256']:assert fixtures[0][n]==fixtures[1][n]
assert fixtures[0]['startup_sha256']!=fixtures[1]['startup_sha256']
names=['fill','upload','readback','screen_overlap','memory_overlap_upload','memory_overlap'];rows=[]
for key,inside in measurements[0].items():
 w,h,kind=key;outside=measurements[1][key]
 rows.append(dict(width=w,height=h,path=names[kind],inside=inside,outside=outside,inside_over_outside=inside['median']/outside['median']))
r=dict(passed=True,physical_access=False,debugger=False,drivers_changed=False,matched_probe_sha256=fixtures[0]['payloads'][0]['sha256'],timings=rows,evidence=evidence,source_sha256=sha(Path(__file__)),limits='Visible standard arrow inside/outside rectangle; same added GetCursorInfo check in both. One ordinary run per placement, three rotated rounds, shared functional slot; no isolated bandwidth/physical FPS claim. Both fixture preparations finished before guest runs. Historical trace31x27 cursor shape need not equal this explicit standard arrow.')
p=k/'pair-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=True,large=[dict(path=v['path'],inside_ms=v['inside']['median'],outside_ms=v['outside']['median'],ratio=v['inside_over_outside']) for v in rows if v['width']==768]),indent=2))
