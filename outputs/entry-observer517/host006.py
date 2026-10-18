"""Call contracts with synthetic frames; not Xbox kernel execution."""
import hashlib,json
from pathlib import Path
from contracts import plan,arguments,returned
K=Path(__file__).resolve().parent;out=K/'host006.json';assert not out.exists()
b=json.loads((K.parent/'entry-colocated516/build001.json').read_text());s=b['wrapper_symbols'];x=Path('C:/xwn516/build001/default.xbe').read_bytes();assert hashlib.sha256(x).hexdigest()==b['sha256']
p=plan(x,s);rejected=accepted=0;h=0x100
for row in p:
 label,_,_,n,ret=row;io=s['entry498_iosb']
 if label=='create':a=[s['entry498_handle'],0x40100000,s['entry498_object'],io,0,0x80,0,2,0x62];iosb=[0,2]
 elif label in ('body','trailer'):a=[h,0,0,0,io,s['entry498_record'] if label=='body' else s['entry498_trailer'],96 if label=='body' else 16,0];iosb=[0,a[-2]]
 elif label.startswith('flush'):a=[h,io];iosb=[0,0]
 else:a=[h];iosb=[0,0]
 w=[ret]+a;assert arguments(row,w,s,h);accepted+=1
 for i in range(len(w)):
  q=w.copy();q[i]^=1
  try:arguments(row,q,s,h)
  except AssertionError:rejected+=1
  else:raise AssertionError('argument mutation accepted')
 before={'ESP':0x1000};after={'ESP':0x1000+4*(n+1),'EAX':0};assert returned(row,before,after,iosb,h);accepted+=1
 for key in after:
  q=dict(after);q[key]^=1
  try:returned(row,before,q,iosb,h)
  except AssertionError:rejected+=1
  else:raise AssertionError('return mutation accepted')
r=dict(passed=True,accepted=accepted,rejected=rejected,actual_XBE_call_sites=p,kernel_frames_modeled=True,physical_access=False,source_sha256=hashlib.sha256((K/'contracts.py').read_bytes()).hexdigest())
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
