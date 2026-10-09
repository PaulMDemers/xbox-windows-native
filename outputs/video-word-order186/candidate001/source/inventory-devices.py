"""Read preserved before/after hives only; no fixture writes or guest access."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;dest=out/'device-inventory.json';assert not dest.exists()
def node(h,path):
 n=h.root()
 for name in path.split('\\'):
  n=h.node_get_child(n,name)
  if not n:return 0
 return n
def values(h,n):
 r={}
 if not n:return r
 for v in h.node_values(n):
  typ,data=h.value_value(v)
  r[h.value_key(v)]=dict(type=typ,hex=data.hex(),decoded=int.from_bytes(data,'little') if typ==4 else data.decode('utf-16le',errors='backslashreplace').rstrip('\0') if typ in [1,2,7] else None)
 return r
r=dict(scope=__doc__,physical_access=False,hives=[])
for phase in ['before','after']:
 p=out/'artifacts'/(phase+'-system');h=hivex.Hivex(str(p));sel=values(h,node(h,'Select'));cs='ControlSet%03d'%sel['Current']['decoded']
 row=dict(phase=phase,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),control_set=cs,devices=[])
 for device in h.node_children(node(h,cs+r'\Enum\PCI')):
  name=h.node_name(device)
  if not (any(name.startswith('VEN_10DE&DEV_'+v) for v in ['01B0','01B4']) or name.startswith('VEN_1B36&DEV_0005')):continue
  for instance in h.node_children(device):
   path=cs+'\\Enum\\PCI\\'+name+'\\'+h.node_name(instance);vals=values(h,instance)
   driver=vals.get('Driver',{}).get('decoded');service=vals.get('Service',{}).get('decoded')
   row['devices'].append(dict(path=path,values=vals,driver_values=values(h,node(h,cs+'\\Control\\Class\\'+driver)) if driver else None,
     service_values=values(h,node(h,cs+'\\Services\\'+service)) if service else None))
 assert len(row['devices']) in [2,3]
 r['hives'].append(row)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps([{key:row[key] for key in ['phase','control_set']} for row in r['hives']]))
