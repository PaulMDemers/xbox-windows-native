"""Compare complete private hives, publishing only changed paths and hashes."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
sha=lambda b:hashlib.sha256(b).hexdigest()
def scan(p):
 h=hivex.Hivex(str(p));r={}
 def walk(n,path):
  r[path]={}
  for v in h.node_values(n):
   t,b=h.value_value(v);r[path][h.value_key(v)]={'type':t,'bytes':len(b),'sha256':sha(b)}
  for c in h.node_children(n):walk(c,path+'\\'+h.node_name(c))
 walk(h.root(),'');return r
a=scan(Path('/mnt/c/xwn839/display-baseline001/system'));b=scan(Path('/mnt/c/xwn839/display-cold001/system'))
diff={p:{'before':a.get(p),'after':b.get(p)} for p in a.keys()|b.keys() if a.get(p)!=b.get(p)}
r={'physical_access':False,'before_keys':len(a),'after_keys':len(b),'changed_keys':diff}
out=K/'system-diff001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'changed_paths':list(diff)},indent=2))
