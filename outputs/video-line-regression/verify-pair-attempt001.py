"""Compare actual ordinary control/candidate pixels and bounded upload volume."""
import copy,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
evidence=read(k.parent/'video-line-bounds/bounds-evidence.json');assert evidence['bounds_evidence_verified'] and not evidence['full_diagnostic_qualified']
checks={n:read(k/n/'verification.json') for n in ['control001','candidate001']}
fixtures={n:read(k/('fixture-'+n+'.json')) for n in checks}
def verify(checks):
 a,b=[checks[n] for n in ['control001','candidate001']]
 assert all(v['passed'] and v['ordinary_qualified'] and v['profile_attribution_passed'] for v in [a,b])
 rows=[]
 for i,(old,new,bounds) in enumerate(zip(a['cases'],b['cases'],evidence['rows'])):
  assert old['index']==new['index']==bounds['sample']==i and old['reference_hash']==new['reference_hash']
  assert old['callbacks']==new['callbacks']==[0]*6+[1]+[0]*7
  assert old['uploads']==new['uploads']==1
  left,top,right,bottom=bounds['bounds'];cl,ct,cr,cb=bounds['clip_bounds']
  want=max(0,min(1024,right,cr)-max(0,left,cl))*max(0,min(576,bottom,cb)-max(0,top,ct))*4
  oldwant=max(0,min(1024,cr)-max(0,cl))*max(0,min(576,cb)-max(0,ct))*4
  assert new['upload_bytes']==want and old['upload_bytes']==oldwant and want<=oldwant
  rows.append(dict(index=i,name=old['name'],old_bytes=oldwant,new_bytes=want,pixels=new['changed_pixels']))
 assert len(rows)==18 and rows[0]['old_bytes']==2359296 and rows[0]['new_bytes']==132
 return rows
rows=verify(checks);rejected=[]
for name in ['cost','pixels','extra_callback','failed_qualification']:
 v=copy.deepcopy(checks)
 if name=='cost':v['candidate001']['cases'][0]['upload_bytes']+=4
 elif name=='pixels':v['candidate001']['cases'][0]['reference_hash']^=1
 elif name=='extra_callback':v['candidate001']['cases'][0]['callbacks'][0]+=1
 else:v['candidate001']['passed']=False
 try:verify(v)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Accepted mutation '+name)
a,b=[fixtures[n] for n in ['control001','candidate001']]
for field in ['parents','protected','preserved_hives','startup_sha256','parent_manifest_sha256','inherited_configuration']:assert a[field]==b[field],field
assert a['payloads'][0]==b['payloads'][0]
review=read(k/'pe-review.json')
assert a['payloads'][1]['sha256']==review['control_display_sha256'] and b['payloads'][1]['sha256']==review['display_sha256']
for i in range(18):assert (k/'control001/artifacts'/('ref%02d.rgb'%i)).read_bytes()==(k/'candidate001/artifacts'/('ref%02d.rgb'%i)).read_bytes()
record=dict(passed=True,ordinary_emulator=True,physical=False,matched_parent_and_probe=True,only_display_payload_differs=True,rows=rows,old_total_bytes=sum(r['old_bytes'] for r in rows),new_total_bytes=sum(r['new_bytes'] for r in rows),short_line_ratio=2359296/132,mutations_rejected=rejected,pins={str(p.relative_to(k)):sha(p) for p in [k/'pe-review.json',k/'control001/verification.json',k/'candidate001/verification.json',k.parent/'video-line-bounds/bounds-evidence.json',Path(__file__)]},limits='Byte volume only; no physical/FPS/actual window-drag claim. Bounds-only debugger evidence is separate from the preserved failed full diagnostic. Broader cursor/mode regression is separate.')
dest=k/'pair-review.json';assert not dest.exists();dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2))
