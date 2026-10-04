"""Read every reachable registry key/value with hivex; never replay or repair.

This validates reachable tree readability, not Windows registry semantics or
orphaned cells. Intended for copies extracted by the cold disk auditor.
"""
from pathlib import Path
import hashlib,sys
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

def audit_hive(path):
 path=Path(path);before=hashlib.sha256(path.read_bytes()).hexdigest()
 h=hivex.Hivex(str(path));stack=[(h.root(),0)];seen=set();values=set();size=0;depth=0
 while stack:
  node,level=stack.pop();assert node not in seen,'Repeated key cell'
  assert level<512 and len(seen)<200000 and len(values)<1000000,'Traversal bound exceeded'
  seen.add(node);depth=max(depth,level);h.node_name(node)
  for value in h.node_values(node):
   assert value not in values,'Repeated value cell'
   values.add(value);h.value_key(value);typ,data=h.value_value(value)
   size+=len(data);assert size<256*1024*1024,'Value data bound exceeded'
  stack.extend((child,level+1) for child in h.node_children(node))
 del h
 assert hashlib.sha256(path.read_bytes()).hexdigest()==before
 return {'scope':'Read-only reachable key/value traversal; no log replay or semantic validation',
         'sha256':before,'keys':len(seen),'values':len(values),'value_bytes':size,
         'maximum_depth':depth,'source_preserved':True,'passed':True}

if __name__=='__main__':
 import json
 print(json.dumps(audit_hive(sys.argv[1])))
