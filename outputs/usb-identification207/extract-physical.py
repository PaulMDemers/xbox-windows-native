"""Read preserved physical189 evidence without changing its hive or providers."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent
base=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((base/'outputs/device-durability189/physical.json').read_text())
row=r['after']['system'];p=base/row['path'];assert sha(p)==row['sha256']
h=hivex.Hivex(str(p));todo=[('',h.root())];nodes={};select={}
while todo:
 path,n=todo.pop()
 if path=='\\Select' or any(t in path.lower() for t in ['\\enum\\usb\\','\\enum\\hid\\','\\enum\\pci\\ven_10de&dev_01c2','\\services\\openhci','\\services\\usbhub','\\services\\hidusb']):
  values={}
  for v in h.node_values(n):
   t,b=h.value_value(v)
   values[h.value_key(v)]={'type':t,'hex':b.hex(),'value':b.decode('utf-16le').rstrip('\0').split('\0') if t in (1,2,7) else int.from_bytes(b,'little') if t==4 else None}
  if path=='\\Select':select=values
  else:nodes[path]=values
 todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
obsp=base/'outputs/device-durability189/physical-observation.json'
obs=json.loads(obsp.read_text());samples=[]
for sample in obs['samples']:
 devices=[]
 for d in sample['devices']:
  if d['instance'].startswith(('USB\\','HID\\')) or 'DEV_01C2' in d['instance']:
   devices.append(dict(instance=d['instance'],status=d['status'],problem=d['problem'],properties={n:bytes.fromhex(v['hex']).decode('ascii').rstrip('\0').split('\0') for n,v in d['properties'].items() if n!='10'}))
 samples.append(dict(index=sample['index'],devices=devices))
result=dict(source=str(p),sha256=sha(p),Select=select,nodes=nodes,present_observation_sha256=sha(obsp),samples=samples,
 limits='Persisted parent-prefix topology plus five live device snapshots; no raw device/configuration/XID descriptors or input reports in this evidence. Historical nodes are not proof of presence.')
(k/'physical-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(hive_sha256=sha(p),select=select,nodes=len(nodes),samples=len(samples))))
