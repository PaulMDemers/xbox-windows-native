"""Reconcile actual bytes/callback evidence; keep host mutations separate."""
import hashlib,json
from pathlib import Path
from protocol import validate_log,expected_bytes,HOOKS
k=Path(__file__).resolve().parent;out=k/'candidate001'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'profile-verification.json';assert not dest.exists()
v=read(k/'verification.json');assert v['passed'] and v['profile_attribution_passed']
raw=(out/'artifacts/result.log').read_bytes();r=validate_log(raw)
assert r['passed'] and r['profile_attribution_passed']
for n in range(18):assert (out/'artifacts'/('ref%02d.rgb'%n)).read_bytes()==expected_bytes(n)
rows=[]
for i in range(6):
 samples=[r['cases'][i+6*j] for j in range(3)];first=samples[0]
 assert all(s['clip']==[0,0,1024,576] for s in samples)
 rows.append(dict(operation=first['name'].rsplit('_',1)[0],samples=[s['index'] for s in samples],changed_pixels=first['changed_pixels'],uploads=first['uploads'],upload_bytes=first['upload_bytes'],actual_callbacks={name:n for name,n in zip(HOOKS,first['callbacks']) if n},bytes_per_changed_pixel=first['upload_bytes']/first['changed_pixels']))
assert rows[1]['upload_bytes']==1024*576*4 and rows[2]['upload_bytes']==32*4
assert (out/'artifacts/ref01.rgb').read_bytes()==(out/'artifacts/ref02.rgb').read_bytes()
assert rows[4]['upload_bytes']==196*156*4
mutations={}
lines=raw.decode('ascii').splitlines()
for name,label,col,delta in [('pixel','PIXELS_BAD_CHANGED',2,1),('quiet','QUIET_COUNTER',2,1),('reference','REFERENCE_COUNTER',2,1),('bytes','DRAW_COUNTER 17',3,4),('clip','CLIP_RIGHT_BOTTOM',1,-1)]:
 copy=lines[:];index=next(i for i,line in enumerate(copy) if line.startswith(label+' '));words=copy[index].split();words[col]=str(int(words[col])+delta);copy[index]=' '.join(words)
 result=validate_log(('\n'.join(copy)+'\n').encode());assert not (result['passed'] and result['profile_attribution_passed']),name
 mutations[name]=True
altered=bytearray((out/'artifacts/ref03.rgb').read_bytes());altered[0]^=1
assert bytes(altered)!=expected_bytes(3);mutations['cold_pixel']=True
record=dict(passed=True,ordinary_emulator=True,physical=False,driver_changed=False,rows=rows,short_line_transfer_ratio=rows[1]['upload_bytes']//rows[2]['upload_bytes'],disjoint_bounding_vs_changed_byte_ratio=rows[4]['upload_bytes']/(rows[4]['changed_pixels']*4),repetitions=3,compared_pixels=r['compared_pixels'],actual_evidence_mutations_rejected=mutations,pins={str(p.relative_to(k)):sha(p) for p in [k/'verification.json',out/'artifacts/result.log',k/'protocol.py',Path(__file__),k/'../video-mode-reset/display/shadow.c']},limits='Global upload counters measure byte volume, not physical bandwidth, timing or actual window dragging. Observed idle/reference intervals were quiet and repeats identical; coincident unrelated drawing is not impossible. Own-driver coherence is not independent physical scanout validation.')
dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
