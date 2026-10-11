"""Exactly two video tokens on freshly captured, genuinely audio-installed SYSTEM."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/native-windows-nt5-kernel'))
from nt5_hive_indexes import normalize
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert read(repo/'outputs/demo-physical252/install001/audit.json')['scoped_installation_passed']
assert read(k/'capture002.json')['passed'] and read(k/'before-audit002.json')['passed']
assert read(k/'before-audit002.json')['aci_device']['service']==['xwnaci207']
dest=k/'binding-edit.json';p=k/'artifacts/proposed-system';assert not dest.exists() and not p.exists()
source=k/'artifacts/before002/F/winnt/system32/config/system';raw=source.read_bytes()
assert sha(raw)==read(k/'capture002.json')['files']['/F/winnt/system32/config/system']['sha256']
def semantic(h):
    keys=set();values={};todo=[('',h.root())]
    while todo:
        path,n=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(n):values[path,h.value_key(v)]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values
p.write_bytes(raw);h=hivex.Hivex(str(p),write=True);keys,values=semantic(h);expected=dict(values)
assert int.from_bytes(values['\\Select','Current'][1],'little')==1
changes=read(repo/'outputs/video-text-oracle206/binding-edit.json')['changes'];assert len(changes)==2
for row in changes:
    key=('\\'+row['path'],row['name']);assert values[key]==(row['type'],bytes.fromhex(row['before_hex']))
    n=h.root()
    for part in row['path'].split('\\'):n=h.node_get_child(n,part);assert n
    data=bytes.fromhex(row['after_hex']);h.node_set_value(n,dict(key=row['name'],t=row['type'],value=data));expected[key]=(row['type'],data)
h.commit(None);del h
data,indexes=normalize(p.read_bytes());p.write_bytes(data);h=hivex.Hivex(str(p));assert semantic(h)==(keys,expected)
dest.write_text(json.dumps(dict(passed=True,changes=changes,only_two_expected_values_changed=True,parent_sha256=sha(raw),after_sha256=sha(data),indexes=indexes,audio_binding_preserved=True),indent=2)+'\n')
print('Fresh post-audio SYSTEM: exactly two reviewed video tokens changed')
