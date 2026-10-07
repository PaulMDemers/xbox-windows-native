"""Summarize only a complete cold-verified fixed-driver profile; never hardware speed."""
import hashlib,json,statistics
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'baseline001'
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
a=read(out/'audit.json');pre=read(out/'preflight.json');c=read(out/'closure.json');f=read(k/'fixture-baseline001.json')
assert a['strict_qualification_passed'] and a['protocol_exact'] and not a['explicit_ui_intervention']
assert not (out/'manual-log-actions.json').exists()
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
assert sha(k/'probe.c')==sha(out/'source/probe.c')==read(k/'build-review.json')['source_sha256']
assert sha(Path(c['private_disk']))==c['private_disk_sha256']
for n,h in c['run_metadata_sha256'].items():assert sha(Path(c['private_disk']).parent/n)==h
assert all(v['matched'] for v in a['protected']+a['payloads']) and all(v['parsed'] for v in a['hives'])
assert len(a['protocol_details']['cases'])==54 and a['protocol_details']['verified_pixel_stages']==162
names=['fill','upload','readback','screen_overlap','memory_overlap_upload','memory_overlap'];rows=[];ratios=[]
for w,h in [(64,64),(256,128),(768,384)]:
 vals={}
 for kind,name in enumerate(names):
  samples=[v for v in a['protocol_details']['cases'] if v['width']==w and v['height']==h and v['kind']==kind];assert len(samples)==3
  times=[v['elapsed_ms']/v['count'] for v in samples];vals[kind]=statistics.median(times)
  rows.append(dict(width=w,height=h,path=name,ms_per_iteration_median=vals[kind],ms_per_iteration_min=min(times),ms_per_iteration_max=max(times),samples=samples))
 ratios.append(dict(width=w,height=h,screen_to_memory_plus_upload_ratio=vals[3]/vals[4],screen_to_memory_only_ratio=vals[3]/vals[5]))
r=dict(passed=True,physical_access=False,driver_changed=False,mode_changed=False,debugger=False,emulator_only=True,pixel_stages=162,timed_cases=54,timings=rows,ratios=ratios,audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),source_sha256=sha(Path(__file__)),limits='One functional emulator slot, three rounds with rotated order. Timings include GdiFlush, message pumping and visibility checks; not physical memory bandwidth, window-drag FPS or statistical hardware speedup. System-memory-copy/upload is an application surrogate, not a shadow display driver.')
p=k/'summary.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,ratios=ratios),indent=2))
