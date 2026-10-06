"""Decode a preserved physical registry snapshot offline; never changes the console."""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, '/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k = Path(__file__).resolve().parent
capture = json.loads((k/'capture.json').read_text())
assert capture['completed']
for item in capture['files']:
    assert hashlib.sha256((k/'artifacts'/item['local']).read_bytes()).hexdigest() == item['sha256']
h = hivex.Hivex(str(k/'artifacts/system'))
def node(path):
    n=h.root()
    for part in path.split('\\'):
        n=h.node_get_child(n,part)
        if not n:return 0
    return n
def values(path):
    n=node(path)
    if not n:return {}
    result={}
    for v in h.node_values(n):
        t,data=h.value_value(v)
        result[h.value_key(v)] = int.from_bytes(data,'little') if t==4 else (data.decode('utf-16le').rstrip('\0') if t in [1,2,7] else data.hex())
    return result
cs='ControlSet%03d'%values('Select')['Current']
devices=[]
base=cs+'\\Enum\\PCI'
for d in h.node_children(node(base)):
    for instance in h.node_children(d):
        path=base+'\\'+h.node_name(d)+'\\'+h.node_name(instance)
        v=values(path);driver=v.get('Driver','')
        devices.append(dict(path=path,values=v,driver_key=values(cs+'\\Control\\Class\\'+driver) if driver else {}))
h=hivex.Hivex(str(k/'artifacts/software'))
devicepath=values(r'Microsoft\Windows\CurrentVersion').get('DevicePath')
text=(k/'artifacts/setupapi.log').read_bytes().decode('cp1252', errors='backslashreplace')
r=dict(scope=__doc__,physical_snapshot=True,remote_writes=False,windows_launch=False,
       capture_sha256=hashlib.sha256((k/'capture.json').read_bytes()).hexdigest(),
       pci_devices=devices,device_path=devicepath,setupapi_tail=text.splitlines()[-110:],
       limits='Registry state alone does not establish an active installer or a current popup; this is a dashboard-time snapshot.')
(k/'decoded-state.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(device_path=devicepath,devices=[dict(id=v['path'],service=v['values'].get('Service'),flags=v['values'].get('ConfigFlags'),description=v['values'].get('DeviceDesc'),driver=v['driver_key'].get('InfPath')) for v in devices]),indent=2))
