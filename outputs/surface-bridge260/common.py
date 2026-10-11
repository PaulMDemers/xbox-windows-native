"""Cold read-only utilities for captured physical-core display reconstruction."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'))
from coldio import ColdIO
from allocation import scan
sys.path.insert(0,str(k.parent/'native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
STARTUP='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
HIVES=['system','software','default','sam','security']
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
def readers(io,disk):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
def hive(path):
    sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
    import hivex
    h=hivex.Hivex(str(path));todo=[h.root()];seen=set();values=0
    while todo:
        n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
        for v in h.node_values(n):h.value_key(v);h.value_value(v);values+=1
        todo.extend(h.node_children(n))
    return dict(parsed=True,keys=len(seen),values=values,sha256=sha(path))
