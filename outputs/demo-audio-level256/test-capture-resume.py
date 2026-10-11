"""Exercise actual nested capture file function without FTP or console access."""
import ast,hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;source=k/'capture-recovery-review.py'
tree=ast.parse(source.read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
filefn=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='file')
compiled=compile(ast.Module(body=[filefn],type_ignores=[]),str(source),'exec')
root=k/'artifacts/capture-resume-test001';root.mkdir(exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
class FakeFTP:
 def __init__(self,data):self.data=data;self.reads=0
 def retrbinary(self,command,write,blocksize):
  assert command=='RETR /F/test.txt';self.reads+=1;write(self.data)
results=[]
for name,old,local,data,fail in [
 ('new',False,False,b'old',False),
 ('cached-same',True,True,b'old',False),
 ('cached-changed',True,True,b'new',True),
 ('missing-local-same',True,False,b'old',False),
 ('missing-local-changed',True,False,b'new',True)]:
 stage=root/name;stage.mkdir();target=stage/'F/test.txt'
 if local:target.parent.mkdir();target.write_bytes(b'old')
 record={'files':{'/F/test.txt':{'bytes':3,'sha256':sha(b'old')}} if old else {}}
 env=dict(STAGE=stage,sha=sha,hashlib=hashlib,r=record,seen_files=set(),save=lambda:None)
 exec(compiled,env);ftp=FakeFTP(data);rejected=False
 try:env['file'](ftp,'/F/test.txt',3)
 except AssertionError:rejected=True
 assert rejected==fail and ftp.reads==1
 assert record['files']['/F/test.txt']['sha256']==sha(b'old')
 if fail and not local:assert not target.exists()
 if target.exists():assert target.read_bytes()==b'old'
 results.append(dict(case=name,rejected=rejected,remote_reads=ftp.reads))
r=dict(passed=True,source_sha256=sha(source.read_bytes()),physical_access=False,cases=results)
(k/'capture-resume-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
