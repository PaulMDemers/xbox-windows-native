"""Read only captured physical SYSTEM metadata and relevant SetupAPI entries."""
import json,sys,hashlib,re,struct
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'fatx0098-soak3'
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
p=old/'artifacts/hives/F__winnt__system32__config__system'
h=hivex.Hivex(str(p));sha=lambda b:hashlib.sha256(b).hexdigest()
audit=json.loads((old/'binary-audit.json').read_text())
assert next(v['sha256'] for v in audit['hives'] if v['path'].lower()=='f/winnt/system32/config/system')==sha(p.read_bytes())
def node(path):
    n=h.root()
    for part in path.split('\\'):
        n=h.node_get_child(n,part)
        if not n:return None
    return n
def values(path):
    n=node(path)
    if not n:return None
    r={}
    for v in h.node_values(n):
        t,b=h.value_value(v)
        r[h.value_key(v)]=dict(type=t,value=int.from_bytes(b,'little') if t==4 else b.decode('utf-16le').rstrip('\0') if t in [1,2,7] else b.hex())
    return r
current=h.value_dword(h.node_get_value(node('Select'),'Current'));prefix='ControlSet%03d\\'%current
data=(old/'artifacts/diagnostics/setupapi.log').read_bytes();text=data.decode('cp1252',errors='backslashreplace')
blocks=re.split(r'(?=^\[\d{4}/)',text,flags=re.M)
recent=[v for v in blocks if v.startswith('[2026/10/06 14:')]
devices=[]
for b in recent:
    found=re.search(r'DevInstall ([^\r\n]+)',b)
    if found:devices.append(dict(id=found[1],values=values(prefix+'Enum\\'+found[1]),setupapi=b))
mounted=values('MountedDevices')
for name,row in (mounted or {}).items():
    if row['type']==3 and len(row['value'])==24:
        raw=bytes.fromhex(row['value']);row['mbr_signature']=raw[:4].hex();row['partition_byte_offset']=struct.unpack('<Q',raw[4:])[0]
r=dict(scope=__doc__,physical_capture=True,system_sha256=sha(p.read_bytes()),setupapi_sha256=sha(data),control_set=current,latest_boot_setupapi=recent,active_client_installer_devices=devices,mounted_devices=mounted,server_parameters=values(prefix+'Services\\LanmanServer\\Parameters'),srv_event_source=values(prefix+'Services\\Eventlog\\System\\Srv'),limits='Read-only post-run capture; no prior SetupAPI snapshot. Active installer is inferred from last logged start, not a captured shutdown process. Device metadata is not proof of causation.')
(k/'physical-inventory.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(devices=devices,mounted_devices=mounted,srv_event_source=r['srv_event_source']),indent=2))
