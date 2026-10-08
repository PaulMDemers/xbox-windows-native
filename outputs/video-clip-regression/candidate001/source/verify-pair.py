"""Verify matched actual pixels, callbacks and region-sized uploads."""
import copy,hashlib,json
from pathlib import Path
from protocol import points
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={name:read(k/name/'verification.json') for name in ['control001','candidate001']}
def verify(values):
 a,b=[values[n] for n in ['control001','candidate001']]
 assert all(v['passed'] and v['ordinary_qualified'] and v['profile_attribution_passed'] for v in [a,b])
 assert len(a['cases'])==len(b['cases'])==18
 rows=[]
 for i,(old,new) in enumerate(zip(a['cases'],b['cases'])):
  kind=i%6;draws=0 if kind==3 else 2 if kind==5 else 1
  assert old['index']==new['index']==i and old['reference_hash']==new['reference_hash']
  assert old['callbacks']==new['callbacks']==[draws]+[0]*13
  assert old['uploads']==draws and new['uploads']==[2,3,2,0,60,4][kind]
  assert old['upload_bytes']==[122304,4096,393216,0,109120,244608][kind]
  expected=len(points(i))*4*(2 if kind==5 else 1)
  assert new['upload_bytes']==expected<=old['upload_bytes']
  assert old['changed_pixels']==new['changed_pixels']==len(points(i))
  rows.append(dict(index=i,name=old['name'],old_bytes=old['upload_bytes'],new_bytes=expected,pixels=len(points(i)),draws=draws))
 return rows
rows=verify(checks);rejected=[]
for name in ['extra_bytes','missing_rectangle','wrong_pixels','extra_callback','failed_gate']:
 v=copy.deepcopy(checks);c=v['candidate001']['cases'][0]
 if name=='extra_bytes':c['upload_bytes']+=4
 elif name=='missing_rectangle':c['uploads']-=1
 elif name=='wrong_pixels':c['reference_hash']^=1
 elif name=='extra_callback':c['callbacks'][1]+=1
 else:v['candidate001']['passed']=False
 try:verify(v)
 except AssertionError:rejected.append(name)
 else:raise AssertionError('Mutation accepted: '+name)
a,b=[read(k/('fixture-'+n+'.json')) for n in ['control001','candidate001']]
for field in ['parents','protected','preserved_hives','startup_sha256','parent_manifest_sha256','inherited_configuration']:
 assert a[field]==b[field],field
assert a['payloads'][0]==b['payloads'][0]
review=read(k/'pe-review.json')
assert a['payloads'][1]['sha256']==review['control_display_sha256'] and b['payloads'][1]['sha256']==review['display_sha256']
for i in range(18):assert (k/'control001/artifacts'/('ref%02d.rgb'%i)).read_bytes()==(k/'candidate001/artifacts'/('ref%02d.rgb'%i)).read_bytes()
dest=k/'pair-review.json';assert not dest.exists()
pins=[k/'pe-review.json',k/'control001/verification.json',k/'candidate001/verification.json',Path(__file__)]
r=dict(passed=True,ordinary_emulator=True,physical=False,matched_parent_and_probe=True,only_display_payload_differs=True,rows=rows,old_total_bytes=sum(x['old_bytes'] for x in rows),new_total_bytes=sum(x['new_bytes'] for x in rows),mutations_rejected=rejected,pins={str(p.relative_to(ws)):sha(p) for p in pins},limits='Exact bytes and pixels, not FPS or hardware speed. Broader GDI/cursor/reset evidence remains separate.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
