"""Mock one-shot controller, including uncertain replies; no network access."""
import importlib.util,json,sys,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent; spec=importlib.util.spec_from_file_location('launch845',K/'launch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Socket:
 def settimeout(self,v):assert v==20
class FTP:
 sends=0;uncertain=False
 def __init__(self):self.sock=Socket()
 def connect(self,host,timeout):assert host=='192.168.50.66' and timeout==15
 def login(self,user,password):pass
 def close(self):pass
 def sendcmd(self,cmd):
  FTP.sends+=1;assert cmd==m.COMMAND
  if FTP.uncertain:raise TimeoutError()
  return '200 ok'
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp);archive=p/'bundle';archive.write_bytes(b'archive');m.ARCHIVE_SHA256=m.sha(b'archive');owner=b'owner';m.OWNER_SHA256=m.sha(owner);m.EXPECTED={'E/Applications/XWNEBoot/default.xbe':m.sha(b'xbe'),'E/Applications/XWNEBoot/freeldr.sys':m.sha(b'loader')}
 files=[{'path':k,'sha256':v,'bytes':len(b'xbe' if k.endswith('.xbe') else b'loader')} for k,v in m.EXPECTED.items()]
 m.bundle.verify=lambda _: {'kind':'windows-e-preview','profile':'e-720p','files':files}
 m.ticket=lambda:None;m.queue=p;m.FTP=FTP
 m.get=lambda ftp,path,size:owner if 'owner843' in path else (b'xbe' if path.endswith('.xbe') else b'loader')
 original=m.Path
 class P(type(Path())):
  def __new__(cls,*args,**kwargs):
   if args and str(args[0])=='C:/xwn820/connection.json':return original(p/'connection.json')
   return original(*args,**kwargs)
 m.Path=P
 (p/'connection.json').write_text(json.dumps({'host':'192.168.50.66','user':'test','password':'test'}))
 for case,uncertain in [('accepted',False),('uncertain',True)]:
  d=p/case;d.mkdir();pre={'completed':True,'physical_writes':False,'archive_sha256':m.ARCHIVE_SHA256,'target_authentication':{'host':'192.168.50.66','owner_sha256':m.OWNER_SHA256},'files':{x['path']:{'target_sha256':x['sha256']} for x in files}}
  (d/'preflight.json').write_text(json.dumps(pre));(d/'apply.jsonl').write_text('\n'.join(json.dumps(x) for x in [{'kind':'start','archive_sha256':m.ARCHIVE_SHA256},{'kind':'complete','path':'E','files':len(files),'launcher_last':True}])+'\n')
  FTP.uncertain=uncertain;sys.argv=['launch.py',str(archive),str(d)];m.main();rows=[json.loads(x) for x in (d/'launch845.jsonl').read_text().splitlines()];assert rows[0]['kind']=='intent' and rows[1]['kind']==('reply_uncertain' if uncertain else 'reply')
  try:m.main();raise AssertionError('repeat accepted')
  except AssertionError as exc:assert 'Prior launch intent' in str(exc)
 assert FTP.sends==2
print('PASS: one accepted, one uncertain, both repeat attempts refused; no network')
