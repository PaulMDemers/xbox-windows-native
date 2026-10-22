"""Exercise one-shot accepted/uncertain transport recording without networking."""
import importlib.util,json,hashlib,socket
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn659/controller001');assert not P.exists();P.mkdir()
spec=importlib.util.spec_from_file_location('controller659',K/'physical.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
out=K/'controller-review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,controller_sha256=hashlib.sha256((K/'physical.py').read_bytes()).hexdigest(),cases=[])
try:
 for uncertain in [False,True]:
  class FTP:
   def __init__(self):self.sock=self;self.calls=0
   def settimeout(self,value):assert value==20
   def sendcmd(self,command):
    assert command==r'SITE EXEC E:\Applications\XWNIndicate659\default.xbe';self.calls+=1
    if uncertain:raise socket.timeout('modeled uncertain reply')
    return '200 launch accepted'
  f=FTP();p=P/('uncertain.json' if uncertain else 'accepted.json');d.request_once(f,p)
  rec=json.loads(p.read_text());assert rec['requested'] and not rec['automatic_retry'] and not rec['test_hook']
  try:d.request_once(f,p)
  except FileExistsError:pass
  else:raise AssertionError('duplicate launch admitted')
  assert f.calls==1 and ('reply_uncertain' in rec)==uncertain
  r['cases'].append(dict(uncertain=uncertain,site_calls=1,second_request_refused=True))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS accepted/uncertain request persistence and duplicate-launch refusal')
