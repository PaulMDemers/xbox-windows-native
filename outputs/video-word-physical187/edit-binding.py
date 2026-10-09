"""Private proposed SYSTEM copy: preserve all keys/types/values except two display tokens."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'outputs/native-windows-nt5-kernel'))
from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
review=json.loads((k/'binding-review.json').read_text());assert review['passed']
before=k/'artifacts/F/winnt/system32/config/system';after=k/'artifacts/proposed-system';dest=k/'binding-edit.json'
assert not after.exists() and not dest.exists()
def sha(b):return hashlib.sha256(b).hexdigest()
def node(h,path):
    n=h.root()
    for p in path.split('\\'):n=h.node_get_child(n,p);assert n,path
    return n
def semantic(h):
    keys=set();values={};pending=[('',h.root())]
    while pending:
        path,n=pending.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(n):values[path,h.value_key(v)]=h.value_value(v)
        pending.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values
raw=before.read_bytes();assert sha(raw)==review['hives']['system']['sha256']
h=hivex.Hivex(str(before));keys,values=semantic(h);del h
after.write_bytes(raw);h=hivex.Hivex(str(after),write=True);expected=dict(values)
changes=[]
for row in review['bindings']:
    path,name=row['path'],row['name'];typ,data=values['\\'+path,name]
    assert typ==7 and data==bytes.fromhex(row['before']['hex'])
    new=b'x\x00w\x00n\x00o\x00w\x00n\x00\x00\x00\x00\x00'
    h.node_set_value(node(h,path),dict(key=name,t=typ,value=new));expected['\\'+path,name]=(typ,new)
    changes.append(dict(path=path,name=name,type=typ,before_hex=data.hex(),after_hex=new.hex()))
h.commit(None);del h
data,indexes=normalize(after.read_bytes());after.write_bytes(data)
h=hivex.Hivex(str(after));newkeys,newvalues=semantic(h);assert keys==newkeys and expected==newvalues
assert len(changes)==2
r=dict(passed=True,scope=__doc__,physical_write=False,launch_attempted=False,before_sha256=sha(raw),after_sha256=sha(data),
       all_keys_checked=len(keys),all_values_checked=len(values),only_two_expected_values_changed=True,changes=changes,index_normalization=indexes)
dest.write_text(json.dumps(r,indent=2)+'\n');print('Private SYSTEM proposal: only two display REG_MULTI_SZ tokens changed; all other keys/values preserved')
