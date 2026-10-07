"""Record inherited unsupported-device state from cold, already collected hives."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent
case=sys.argv[1];assert case in ['001','002','003','004']
path=k/case/'artifacts/after-system';h=hivex.Hivex(str(path))
def values(n):
    r={}
    for v in h.node_values(n):
        t,b=h.value_value(v);r[h.value_key(v)]=int.from_bytes(b,'little') if t==4 else b.decode('utf-16le').rstrip('\0') if t in [1,2,7] else b.hex()
    return r
select=h.node_get_child(h.root(),'Select');cs='ControlSet%03d'%values(select)['Current']
n=h.root()
for part in [cs,'Enum','PCI']:n=h.node_get_child(n,part);assert n
rows=[]
for device in h.node_children(n):
    for instance in h.node_children(device):
        v=values(instance)
        rows.append(dict(id=h.node_name(device)+'\\'+h.node_name(instance),service=v.get('Service'),driver=v.get('Driver'),config_flags=v.get('ConfigFlags'),description=v.get('DeviceDesc')))
r=dict(scope=__doc__,case=case,system_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),devices=rows,
       limits='Offline enum includes historical entries. Inherited failed-install flags are not a driver implementation or hardware qualification. This experiment does not add those flags.')
(k/case/'device-inventory.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps([v for v in rows if v['config_flags'] or not v['service']],indent=2))
