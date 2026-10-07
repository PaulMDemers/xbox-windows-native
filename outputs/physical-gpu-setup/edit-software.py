"""Edit only the GPU package search path in a private copy of current physical SOFTWARE."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'outputs/native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
art=k/'artifacts';before=art/'before-software';edit=art/'edited-software';assert not edit.exists()
def digest(b):return hashlib.sha256(b).hexdigest()
def node(h,path):
 n=h.root()
 for part in path.split('\\'):n=h.node_get_child(n,part);assert n,path
 return n
def semantic(h):
 keys=set();values={};pending=[('',h.root())]
 while pending:
  path,n=pending.pop();keys.add(path)
  for v in h.node_values(n):values[(path,h.value_key(v))]=h.value_value(v)
  pending.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
 return keys,values
raw=before.read_bytes();h=hivex.Hivex(str(before));keys,values=semantic(h);path=r'Microsoft\Windows\CurrentVersion';old=h.value_string(h.node_get_value(node(h,path),'DevicePath'));assert 'xwninf102' not in old.lower();new=old+r';C:\xwninf102';del h
edit.write_bytes(raw);h=hivex.Hivex(str(edit),write=True);value=new.encode('utf-16le')+b'\0\0';h.node_set_value(node(h,path),dict(key='DevicePath',t=2,value=value));h.commit(None);del h
data,indexes=normalize(edit.read_bytes());edit.write_bytes(data);h=hivex.Hivex(str(edit));newkeys,newvalues=semantic(h);expected=dict(values);expected[('\\'+path,'DevicePath')]=(2,value);assert keys==newkeys and expected==newvalues
r=dict(scope=__doc__,before_sha256=digest(raw),after_sha256=digest(data),before=old,after=new,all_keys_checked=len(keys),all_values_checked=len(values),only_expected_value_changed=True,index_normalization=indexes,physical_write=False)
(k/'software-edit.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
