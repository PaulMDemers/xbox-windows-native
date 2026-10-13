"""Read-only local capture verification and current hive/volume configuration."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'capture-review001.json'
assert not out.exists()
record=json.loads((K/'capture001.json').read_text());assert record['complete'] and not record['physical_writes'] and not record['console_c_accessed']
P=Path('/mnt/e/xwn337/capture001');sha=lambda b:hashlib.sha256(b).hexdigest()
rows=record['files'];paths={p.lower():p for p in rows}
for path,v in rows.items():
    b=(P/path.lstrip('/')).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256'],path
policy=json.loads((W/'tools/hd-overlay-0.2.0.json').read_text());baseline={}
for path,v in policy['baseline_files'].items():
    actual=paths[path.lower()];baseline[path]=rows[actual]==v
assert all(baseline.values())
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import hive
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
hives={n:hive(P/'F/winnt/system32/config'/n) for n in ['system','software','sam','security','default']}
h=hivex.Hivex(str(P/'F/winnt/system32/config/system'))
def values(path):
    node=h.root()
    for part in path.split('\\'):node=h.node_get_child(node,part);assert node,path
    return {h.value_key(v):{'type':h.value_value(v)[0],'hex':h.value_value(v)[1].hex()} for v in h.node_values(node)}
mounted=values('MountedDevices');select=values('Select');cs='ControlSet%03d'%int.from_bytes(bytes.fromhex(select['Current']['hex']),'little')
memory=values(cs+'\\Control\\Session Manager\\Memory Management')
paging=bytes.fromhex(memory['PagingFiles']['hex']).decode('utf-16le').rstrip('\0').split('\0')
startup='/F/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
result=dict(passed=True,local_read_only=True,physical_writes=False,console_c_accessed=False,files_rehashed=len(rows),logical_bytes=sum(v['bytes'] for v in rows.values()),baseline_files=baseline,hives=hives,mounted_devices=mounted,paging_files=paging,startup_sha256=rows[paths[startup]]['sha256'],capture_sha256=sha((K/'capture001.json').read_bytes()),limits='Capture/input verification only; no staged E install or boot qualification.')
out.write_text(json.dumps(result,indent=2)+'\n');print('Verified',len(rows),'captured files and',len(baseline),'baseline prerequisites; paging',paging)
