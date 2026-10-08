"""Independent geometry prediction for this probe's four full-redraw operations."""
import copy,hashlib,json
from pathlib import Path
from protocol import POSITIONS
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rect(l,t,r,b):return {(x,y) for y in range(max(0,t),min(576,b)) for x in range(max(0,l),min(1024,r))}
def bbox(p):return 0 if not p else (max(x for x,y in p)-min(x for x,y in p)+1)*(max(y for x,y in p)-min(y for x,y in p)+1)
def verify(a,b):
 assert a['passed'] and b['passed']
 bg=rect(0,0,384,256);block=rect(144,56,240,200);rows=[]
 for n in range(18):
  l,t=POSITIONS[n%6];mover=rect(l,t,l+128,t+80);text=rect(l+8,t+24,l+104,t+39)&mover
  # Parent bitmap; visible moving bitmap; fixed solid block; NT5 text bounds.
  regions=[bg-mover-block,mover-block,block,text-block]
  old=sum(bbox(r)*4 for r in regions);new=sum(len(r)*4 for r in regions)
  x=a['cases'][n]['redraw'];y=b['cases'][n]['redraw']
  assert x['callbacks']==y['callbacks']==[1,2,1]+[0]*11
  assert old==x['upload_bytes'] and new==y['upload_bytes']
  rows.append(dict(index=n,old_predicted_bytes=old,new_predicted_bytes=new,per_operation_visible_bytes=[len(r)*4 for r in regions]))
 return rows
if __name__=='__main__':
 dest=k/'redraw-model.json';assert not dest.exists()
 a,b=[read(k/c/'verification.json') for c in ['control001','candidate001']]
 assert read(k/'pair-review.json')['passed']
 for c in ['control001','candidate001']:
  assert read(k/c/'audit.json')['protocol_details']['source_metadata'][:2]==[96,15]
 rows=verify(a,b);bad=copy.deepcopy(b);bad['cases'][0]['redraw']['upload_bytes']+=4
 try:verify(a,bad)
 except AssertionError:rejected=True
 else:raise AssertionError('Accepted incorrect observed byte count')
 r=dict(passed=True,cases=18,rows=rows,rejected_byte_mutation=rejected,pins={c:sha(k/c/'verification.json') for c in ['control001','candidate001']},source_sha256=sha(Path(__file__)),limits='Geometry prediction exactly matches aggregate bytes for these known full-redraw operations. No per-hook runtime tracing, bandwidth, FPS or other-application claim. The mover in position4 extends20rows beyond the readback ROI but inside the1024x576 screen; bytes for that visible extension are included. Readback pixel qualification covers384x256 only.')
 dest.write_text(json.dumps(r,indent=2)+'\n');print('18 full redraws match both bounding-box and exact-visible-region predictions')
