"""Read-only review of two closed owned diagnostics and verified local offload."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=k/'evidence-review.json';assert not dest.exists()
r=dict(physical_access=False,ordinary_qualified=False,performance_qualified=False,cases=[],pins={})
for num in [168,169]:
 kit=k.parent/('video-process-lifecycle'+str(num));case=kit/'candidate001';run=ws/'work/runs'/('nt5-vlife'+str(num)+'-candidate001')
 closed=read(case/'closure.json');assert closed['closed'] and not closed['ordinary_qualified'] and closed['source_snapshot_exact']
 assert sha(run/'cleanup.json')==closed['cleanup_sha256'] and sha(case/'audit.json')==closed['audit_sha256']
 for path,digest in read(kit/'frozen-inputs.json').items():assert sha(ws/path)==digest,path
 for p in (case/'source').iterdir():assert p.read_bytes()==(kit/p.name).read_bytes()
 audit=read(case/'audit.json');v=read(case/'trace-verification.json');assert audit['workload_passed'] and audit['integrity_passed'] and v['teardown_passed']
 assert len(audit['warnings_errors'])==1 and audit['warnings_errors'][0]['source']=='Ftdisk' and audit['warnings_errors'][0]['event_id']==49
 assert not audit['strict_qualification_passed']
 if num==168:assert not v['diagnostic_capture_complete'] and len(v['popups'])==2 and v['creation_entries']==0
 else:assert v['diagnostic_capture_complete'] and not v['popups'] and v['creation_entries']==24 and len(v['creation_pairs'])==24 and len(v['rundll32_pairs'])==2
 for p in [case/'closure.json',case/'audit.json',case/'trace.json',case/'trace-verification.json',kit/'REPORT.md',kit/'NEXT.md']:
  r['pins'][str(p.relative_to(ws)).replace('\\','/')]=sha(p)
 r['cases'].append(dict(kit=kit.name,workload_passed=True,integrity_passed=True,strict_passed=False,capture_complete=v['diagnostic_capture_complete']))
for p in [k/'inventory-devices.py',k/'candidate001/device-inventory.json',k/'TIMING-PLAN.md',k/'timing-interface.json',k/'review-evidence.py',k.parent/'task-storage-offload/Offload-20261008e.ps1',k.parent/'task-storage-offload/manifest-20261008e.json']:
 r['pins'][str(p.relative_to(ws)).replace('\\','/')]=sha(p)
off=read(k.parent/'task-storage-offload/manifest-20261008e.json');assert len(off['records'])==2 and all(v['status']=='complete' for v in off['records'])
for row in off['records']:
 for f in row['files']:
  a=Path(row['source'])/f['path'];b=Path(row['target'])/f['path']
  assert a.stat().st_size==b.stat().st_size==f['bytes'] and sha(a)==sha(b)==f['sha256']
r['passed']=True;dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['cases']))
