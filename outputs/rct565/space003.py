import importlib.util,json,socket
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('p565space3',K.parent/'windows-pair532/controller.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
r=dict(utc=p.m.utc(),writes=[],lines=[])
f=p.m.connect(timeout=5)
try:
 r['cwd_reply']=f.cwd('/E');f.putcmd('HELP')
 for i in range(50):
  try:line=f.getline()
  except socket.timeout:r['bounded_read_timeout']=True;break
  r['lines'].append(line)
  if i and line.startswith('214 '):break
finally:
 f.close();(K/'space003.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
