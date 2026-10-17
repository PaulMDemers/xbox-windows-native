"""Single standalone comparison; Windows installation and launcher are untouched."""
import json,sys,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn430')
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect,get,put,names,sha,utc,write_json,NORMAL,TARGET
from oracle import verify_pixels
REMOTE='/E/Applications/XWNField430'
def stage():
 out=K/'physical001-stage.json';assert not out.exists()
 review=json.loads((K/'review001.json').read_text());assert review['passed']
 exe=(P/'build002/bin/default.xbe').read_bytes();assert sha(exe)==review['xbe_sha256']
 r=dict(utc=utc(),completed=False,console_C_accessed=False,windows_changes=False)
 write_json(out,r)
 with connect() as f:
  baseline(f,'720p');assert 'xwnfield430' not in {n.lower() for n in names(f,'/E/Applications')}
  assert get(f,'/E/documents and settings/all users/start menu/programs/startup/xwn428.cmd',True) is None
  r['normal_startup_sha256']=sha(get(f,NORMAL));r['launcher_sha256']=sha(get(f,TARGET))
  f.mkd(REMOTE);put(f,REMOTE+'/default.xbe',exe)
  assert get(f,REMOTE+'/default.xbe')==exe
  r.update(completed=True,xbe_sha256=sha(exe));write_json(out,r)
def launch():
 out=K/'physical001-launch.json';assert not out.exists()
 r=json.loads((K/'physical001-stage.json').read_text());assert r['completed']
 with connect() as f:
  baseline(f,'720p');assert sha(get(f,REMOTE+'/default.xbe'))==r['xbe_sha256']
  assert set(names(f,REMOTE))=={'default.xbe'}
  r=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNField430\default.xbe')
  write_json(out,r);f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as exc:r['uncertain_reply']=type(exc).__name__
  write_json(out,r)
def verify(data):
 if len(data)!=1280:raise ValueError('record length')
 rows=[struct.unpack('<32I',data[i:i+128]) for i in range(0,len(data),128)]
 if any(r[:2]!=(0x430c0de,1) for r in rows):raise ValueError('identity')
 if rows[0][3]!=99 or rows[-1][2:4]!=(0,100):raise ValueError('terminal failure')
 for i,r in enumerate(rows[1:9]):
  m,p=divmod(i,4);w,h=(1280,720) if m==0 else (1920,1080)
  if r[2:6]!=(m,p,w,h) or r[10]!=0:raise ValueError('stage')
  if not (r[8]>=w*h*4 and 1<=r[11]<=250 and 9000<=r[12]<=30000):raise ValueError('coverage')
  if not (32<=r[14]<=111 and 32<=r[15]<=95):raise ValueError('bounds')
 return rows
def collect():
 out=K/'physical001-collection.json';assert not out.exists()
 private=P/'physical001';assert not private.exists();private.mkdir()
 r=dict(utc=utc(),completed=False,files={},console_C_accessed=False)
 write_json(out,r)
 try:
  stage=json.loads((K/'physical001-stage.json').read_text())
  with connect() as f:
   baseline(f,'720p');assert sha(get(f,NORMAL))==stage['normal_startup_sha256']
   assert sha(get(f,TARGET))==stage['launcher_sha256']
   for name in names(f,REMOTE):
    assert '/' not in name and '\\' not in name
    b=get(f,REMOTE+'/'+name);assert b==get(f,REMOTE+'/'+name)
    (private/name).write_bytes(b);r['files'][name]=dict(bytes=len(b),sha256=sha(b));write_json(out,r)
  r['rows']=verify((private/'result.bin').read_bytes())
  r['pixels_verified']=sum(verify_pixels((private/('capture-%d.bgrx'%i)).read_bytes(),i%4) for i in range(8))
  r.update(completed=True,scoped_cpu_readback_passed=True,signal_qualified=False,full_allocation_audit=False)
 except Exception as exc:r['failure']=repr(exc);raise
 finally:write_json(out,r)
 print(json.dumps({n:r[n] for n in ('completed','pixels_verified')}))
if __name__=='__main__':
 action=sys.argv[1];assert action in ('stage','launch','collect');globals()[action]()
