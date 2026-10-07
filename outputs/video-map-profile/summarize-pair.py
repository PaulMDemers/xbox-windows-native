"""Verify matched closed cases and summarize emulator-only timings."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
host=lambda s:Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cases=['control001','candidate001'];fs=[];audits=[];medians=[];rows=[]
for case in cases:
 out=k/case;a=read(out/'audit.json');pre=read(out/'preflight.json');c=read(out/'closure.json');f=read(k/('fixture-'+case+'.json'))
 assert a['strict_qualification_passed'] and not a['debugger'] and not a['explicit_ui_intervention']
 assert sha(Path(c['private_disk']))==c['private_disk_sha256']
 for n,h in c['run_metadata_sha256'].items():assert sha(Path(c['private_disk']).parent/n)==h
 for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
 for p in f['parents']:assert sha(host(p['path']))==p['sha256']
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
 before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
 for n in ['clusters','file_size','first_cluster','whole_file','requested_65536']:assert before[n]==after[n]
 assert all(read(out/(phase+'-configuration.json'))['expected_configuration'] for phase in ['before','after'])
 assert len(a['protocol_details']['cases'])==54 and a['protocol_details']['verified_pixel_stages']==162
 assert all(v['elapsed_ms']>=300 or v['count']==4096 for v in a['protocol_details']['cases'])
 vals={}
 for w,h in [(64,64),(256,128),(768,384)]:
  for kind in range(6):
   samples=[v for v in a['protocol_details']['cases'] if v['width']==w and v['height']==h and v['kind']==kind];assert len(samples)==3
   times=[v['elapsed_ms']/v['count'] for v in samples];vals[(w,h,kind)]=statistics.median(times)
 fs.append(f);audits.append(a);medians.append(vals)
for n in ['parents','preserved_hives','payloads','startup_sha256','initial_trace_sha256','build_review_sha256','parent_manifest_sha256']:assert fs[0][n]==fs[1][n]
diff=[]
for a,b in zip(fs[0]['protected'],fs[1]['protected']):
 assert (a['volume'],a['path'])==(b['volume'],b['path'])
 if a!=b:diff.append(a['path'])
assert diff==['winnt/system32/drivers/xboxvnt5.sys']
mapping=read(k/'candidate001/mapping.json');assert mapping['trace_sha256']==audits[1]['trace_sha256']
assert sha(k/'candidate001/artifacts/video-trace.bin')==mapping['trace_sha256']
for group in mapping['mapping_observations']:
 assert group['physical']==0x3c00000 and group['length']==0x400000
 for tag,pa in [('0',0x3c00000),('1',0x3fff000)]:
  page=group['pages'][tag];assert page['present'] and page['physical']==pa and page['effective_type']=='UC'
names=['fill','upload','readback','screen_overlap','memory_overlap_upload','memory_overlap']
for key,v in medians[0].items():
 w,h,kind=key;c=medians[1][key]
 rows.append(dict(width=w,height=h,path=names[kind],control_ms=v,candidate_ms=c,control_over_candidate=v/c))
r=dict(passed=True,postprocessor_sha256=sha(Path(__file__)),host_workload_caveat='Candidate preparation/cold reads overlapped part of control runtime. Both are functional shared-slot measurements, not isolated benchmarks.',physical_access=False,debugger=False,cases=cases,strict_results=[a['strict_qualification_passed'] for a in audits],changed_protected_files=diff,matched_probe_sha256=fs[0]['payloads'][0]['sha256'],timings=rows,mapping_sha256=sha(k/'candidate001/mapping.json'),evidence={case:{n:sha(k/case/n) for n in ['audit.json','closure.json','preflight.json','before-configuration.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json']} for case in cases},limitations='Emulator API timings, not hardware speed or drag FPS. One run per binary, three rotated rounds, shared functional slot.0096 also adds mapping/lifetime instrumentation relative to0093; not a single-instruction comparison. Exact GDI self-readback is not independent scanout. Generic PnP stop/remove/restart and physical direct mapping remain unqualified.')
p=k/'pair-review.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,large=[v for v in rows if v['width']==768]),indent=2))
