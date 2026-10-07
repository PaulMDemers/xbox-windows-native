"""Read all persistent display selector values; never edits hives or fixtures."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(physical_access=False,read_only=True,source_sha256=sha(Path(__file__)),hives=[])
for case in ['control001','candidate001']:
 for phase,name in [('prepared','prepared-system'),('after','after-system')]:
  p=k/case/'artifacts'/name;h=hivex.Hivex(str(p));todo=[('',h.root())];rows=[]
  while todo:
   path,node=todo.pop()
   for v in h.node_values(node):
    key=h.value_key(v);typ,data=h.value_value(v)
    if key.lower() in ['installeddisplaydrivers','videokey','service'] and (key.lower()=='installeddisplaydrivers' or '\\Control\\Video\\'.lower() in path.lower()):
     rows.append(dict(path=path,key=key,type=typ,value=data.decode('utf-16le').rstrip('\0') if typ in [1,2,7] else data.hex(),raw=data.hex()))
   todo.extend((path+'\\'+h.node_name(n),n) for n in h.node_children(node))
  r['hives'].append(dict(case=case,phase=phase,sha256=sha(p),selectors=rows))
dest=k/'selection-inventory.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
