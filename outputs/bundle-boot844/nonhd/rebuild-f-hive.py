from pathlib import Path
import sys,struct,json,hashlib,os
K=Path(__file__).resolve().parent;W=K.parents[2];P=Path(os.environ['XWN_HIVE_OUTPUT']);assert not P.exists();P.mkdir();source=Path(os.environ['XWN_HIVE_SOURCE']);raw=source.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='b34f4798ae5b1ea7c3acc461922b91eb315a106f2a948007e846688fdb49364d'
import hivex
sys.path.insert(0,str(W/'outputs/native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
def semantic(h):
 q=[('',h.root())];k=set();v={}
 while q:
  path,n=q.pop();assert path not in k;k.add(path)
  for x in h.node_values(n):v[path,h.value_key(x)]=h.value_value(x)
  q.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
 return k,v
h=hivex.Hivex(str(source));keys,values=semantic(h);del h;out=P/'system';out.write_bytes(raw);h=hivex.Hivex(str(out),write=True);node=h.node_get_child(h.root(),'MountedDevices');e=struct.pack('<IQ',0xaa55,5633024*512);f=struct.pack('<IQ',0xaa55,15633072*512);changed=[];expected=dict(values)
for x in [(h.value_key(v),*h.value_value(v)) for v in h.node_values(node)]:
 key,typ,data=x
 if data in (e,f):
  new=f if data==e else e;h.node_set_value(node,dict(key=key,t=typ,value=new));expected['\\MountedDevices',key]=(typ,new);changed.append(key)
assert len(changed)==4 and expected['\\MountedDevices','\\DosDevices\\C:']==(3,e) and expected['\\MountedDevices','\\DosDevices\\D:']==(3,f)
h.commit(None);del h;fixed,indexes=normalize(out.read_bytes());out.write_bytes(fixed);h=hivex.Hivex(str(out));k2,v2=semantic(h);assert k2==keys and v2==expected;del h
(P/'private-hive-report.json').write_text(json.dumps({'passed':True,'before_sha256':sha(raw),'after_sha256':sha(fixed),'keys_checked':len(keys),'values_checked':len(values),'changed_mounteddevices':changed,'normalization':indexes,'scope':'0.1.0 physical F snapshot offline E-root adaptation; exactly E/F volume identities swapped, all other semantic values unchanged, no boot qualification.'},indent=2)+'\n')
