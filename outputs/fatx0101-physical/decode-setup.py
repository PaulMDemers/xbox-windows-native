"""Offline post-trial device registration and SetupAPI evidence; no console writes."""
import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
audit=json.loads((k/'binary-audit.json').read_text());assert audit['complete']
entry=next(v for v in audit['hives'] if v['path']=='F/winnt/system32/config/system')
source=k/'artifacts/hives/F__winnt__system32__config__system';assert sha(source.read_bytes())==entry['sha256']
h=hivex.Hivex(str(source))
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
        result[h.value_key(v)]=int.from_bytes(data,'little') if t==4 else data.decode('utf-16le').rstrip('\0') if t in [1,2,7] else data.hex()
    return result
cs='ControlSet%03d'%values('Select')['Current'];devices=[]
for bus in ['PCI','USB','HID']:
    base=cs+'\\Enum\\'+bus;n=node(base)
    if not n:continue
    for device in h.node_children(n):
        for instance in h.node_children(device):
            path=base+'\\'+h.node_name(device)+'\\'+h.node_name(instance)
            v=values(path);driver=v.get('Driver','')
            devices.append(dict(path=path,values=v,driver_key=values(cs+'\\Control\\Class\\'+driver) if driver else {}))
trial=json.loads((k/'physical.json').read_text());raw=(k/'artifacts/physical/after-setupapi.log').read_bytes()
assert sha(raw)==trial['collected']['setupapi.log']['sha256']
prior=k.parent/'physical-pnp-followup';capture=json.loads((prior/'capture.json').read_text())
old=(prior/'artifacts/setupapi.log').read_bytes();assert sha(old)==next(v['sha256'] for v in capture['files'] if v['local']=='setupapi.log')
prefix=raw.startswith(old);text=(raw[len(old):] if prefix else raw).decode('cp1252',errors='backslashreplace')
sections=[]
for chunk in re.split(r'(?=^\[\d{4}/)',text,flags=re.M):
    lines=chunk.splitlines()
    if not lines:continue
    interesting=[v for v in lines if any(t.lower() in v.lower() for t in ['client install','Munged cmdline','EXE name','hardware ID','finished successfully','compatible driver','error','failed','select device','cancel'])]
    if interesting:sections.append(dict(header=lines[0],lines=interesting))
before=json.loads((prior/'decoded-state.json').read_text())
oldpci={v['path']:v for v in before['pci_devices']}
changes=[dict(path=v['path'],before=oldpci.get(v['path']),after=v) for v in devices if '\\Enum\\PCI\\' in v['path'] and oldpci.get(v['path'])!=v]
r=dict(scope=__doc__,system_sha256=sha(source.read_bytes()),setupapi_sha256=sha(raw),prior_capture_utc=capture['utc'],prior_setupapi_exact_prefix=prefix,devices=devices,pci_changes_since_prior_snapshot=changes,setupapi_sections_since_prior_snapshot=sections,limits='Prior snapshot predates this trial; changes are interval observations, not causal attribution. Registry entries include history and are not live bus inventory or proof the installation queue is idle. Successful HID install does not imply vendor-specific features work.')
(k/'setup-state.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(prior_prefix=prefix,pci_changes=len(changes),devices=[dict(path=v['path'],service=v['values'].get('Service'),flags=v['values'].get('ConfigFlags'),inf=v['driver_key'].get('InfPath')) for v in devices if 'VEN_10DE' in v['path'].upper() or 'VID_1532' in v['path'].upper()]),indent=2))
