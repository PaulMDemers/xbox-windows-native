"""Inspect collected setup hives and identify malformed log bytes before the authorized second boot."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
case=sys.argv[1] if len(sys.argv)>1 else '001';assert case in ['001','002']
target=k if case=='001' else k/'002';art=target/'artifacts';result={'scope':__doc__,'case':case,'hives':{}}
def vals(h,n):
 out={}
 for v in h.node_values(n):
  t,b=h.value_value(v);out[h.value_key(v)]=int.from_bytes(b,'little') if t==4 else b.decode('utf-16le').rstrip('\0') if t in (1,2,7) else b.hex()
 return out
def node(h,path):
 n=h.root()
 for part in path.split('\\'):n=h.node_get_child(n,part);assert n,path
 return n
for name in ['system','software']:
 p=art/('after-'+name);h=hivex.Hivex(str(p));q=[h.root()];seen=set();count=0
 while q:
  n=q.pop();assert n not in seen;seen.add(n);h.node_name(n)
  for v in h.node_values(n):h.value_key(v);h.value_value(v);count+=1
  q.extend(h.node_children(n))
 result['hives'][name]=dict(keys=len(seen),values=count,structural_walk_passed=True,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 if name=='system':
  cs='ControlSet%03d'%vals(h,node(h,'Select'))['Current'];base=cs+r'\Enum\PCI';devices=[]
  for dev in h.node_children(node(h,base)):
   if not h.node_name(dev).startswith('VEN_10DE&DEV_02A0'):continue
   for inst in h.node_children(dev):
    v=vals(h,inst);driver=v.get('Driver');devices.append(dict(path=base+'\\'+h.node_name(dev)+'\\'+h.node_name(inst),values=v,driver_key=vals(h,node(h,cs+'\\Control\\Class\\'+driver)) if driver else {}))
  result['gpu']=devices;result['service']=vals(h,node(h,cs+r'\Services\XboxVnt5'))
 else:result['device_path']=vals(h,node(h,r'Microsoft\Windows\CurrentVersion'))['DevicePath']
before=((k/'artifacts/before-setupapi.log') if case=='001' else (k/'artifacts/after-setupapi.log')).read_bytes();after=(art/'after-setupapi.log').read_bytes();result['setupapi_prior_exact_prefix']=after.startswith(before);new=after[len(before):] if after.startswith(before) else after
bad=[i for i,b in enumerate(new) if b not in (9,10,13) and not 32<=b<127];result['new_log_non_ascii_count']=len(bad);result['new_log_non_ascii_range']=[min(bad),max(bad)] if bad else None
result['setupapi_success_record']=b'Device install finished successfully (PCI\\VEN_10DE&DEV_02A0' in new
result['qualification']='Incomplete setup experiment; malformed SetupAPI bytes preserved and unresolved, not a clean PASS'
(target/('first-setup-review.json' if case=='001' else 'setup-state-review.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
