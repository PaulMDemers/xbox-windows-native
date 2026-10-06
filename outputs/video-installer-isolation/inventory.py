"""Read baseline PCI installation metadata; missing Service alone does not prove a queued installer."""
import json,sys
from pathlib import Path
k=Path(__file__).resolve().parent
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
h=hivex.Hivex(str(k/'audio003/artifacts/before-system'))
def node(path):
 n=h.root()
 for part in path.split('\\'):n=h.node_get_child(n,part);assert n
 return n
current=h.value_dword(h.node_get_value(node('Select'),'Current'))
root=node('ControlSet%03d\\Enum\\PCI'%current);rows=[]
for device in h.node_children(root):
 for instance in h.node_children(device):
  values={}
  for v in h.node_values(instance):
   name=h.value_key(v)
   if name not in ['DeviceDesc','Class','ClassGUID','Service','Driver','ConfigFlags','HardwareID']:continue
   t,data=h.value_value(v)
   values[name]=int.from_bytes(data,'little') if t==4 else data.decode('utf-16le').rstrip('\0') if t in [1,2,7] else data.hex()
  rows.append(dict(instance='PCI\\'+h.node_name(device)+'\\'+h.node_name(instance),values=values))
report=dict(scope=__doc__,physical_access=False,control_set=current,devices=rows)
(k/'baseline-pci.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([v for v in rows if 'Service' not in v['values']],indent=2))
