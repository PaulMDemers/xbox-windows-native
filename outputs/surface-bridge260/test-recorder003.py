"""Exercise exact003 failure recorder and actual prior HMP IDTR formatting."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'recorder-review003.json';assert not dest.exists()
tree=ast.parse((k/'trace003.py').read_text());func=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='observed_read')
class Remote:
 def __init__(self,error=False):self.error=error
 def read(self,a,n):
  if self.error:raise AssertionError('E14')
  return b'X'*n
for fail in [False,True]:
 saved=[];row={'reads':[]};walks=[]
 def translate(physical,cr3,cr4,a,forbidden):walks.append((a,forbidden));return 0x2000,{'pde':1}
 env=dict(stopped=True,row=row,save=lambda:saved.append(json.loads(json.dumps(row))),g=Remote(fail),hashlib=hashlib,translate32=translate,physical_read=lambda a,n:(_ for _ in ()).throw(AssertionError('No physical payload')),registers={'cr3':0,'cr4':0})
 exec(compile(ast.fix_missing_locations(ast.Module(body=[func],type_ignores=[])),'actual-trace003-function','exec'),env)
 try:result=env['observed_read'](0x823d0000,16)
 except AssertionError:assert fail and row['reads'][0]['error']=="AssertionError('E14')" and len(walks)==1
 else:assert not fail and result==b'X'*16 and not walks
 assert saved[0]['reads'][0]['status']=='requested' and saved[-1]['reads'][0]['status']==('failed' if fail else 'read')
raw=json.loads((k/'emu002/trace.json').read_text());text=next(x['reply'] for x in raw['monitor'] if x['command']=='info registers');m=re.search(r'IDT=\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',text);assert [int(v,16) for v in m.groups()]==[0x828cb400,0x7ff]
r=dict(passed=True,read_recorder_paths=2,prior_actual_idtr_format=True,guest_ownership_proved=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),trace_sha256=hashlib.sha256((k/'trace003.py').read_bytes()).hexdigest())
dest.write_text(json.dumps(r,indent=2)+'\n');print('003 exact recorder success/error paths and actual HMP format PASS')
