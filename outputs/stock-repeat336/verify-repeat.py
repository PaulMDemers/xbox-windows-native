"""Require unchanged first-boot artifacts and persisted Windows C binding after boot2."""
import json,sys,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'emu001';dest=out/'repeat-proof.json';assert not dest.exists()
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha
from stock_io002 import readers
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
p=json.loads((out/'preparation.json').read_text());a=json.loads((out/'audit.json').read_text());assert p['prepared']
disk=Path('/mnt/e/xwn336/runs/nt5-stock336-emu001/hdd.qcow2');assert (disk.parent/'cleanup.json').exists()
r=dict(passed=False,physical_access=False,files=[],offline_hive_edit_between_boots=p['registry_edited'])
with ColdIO(disk) as io:
    e=readers(io,disk)['E']
    for name,digest in p['retained_first_boot_files'].items():
        actual=m.sha(e.read(name));r['files'].append(dict(path=name,before=digest,after=actual,matched=digest==actual))
    io.seek(0);r['no_extended_partition_table']=io.read(512)==bytes(512)
    io.seek(15633072*512);r['no_F_filesystem']=io.read(4)!=b'FATX'
maps={}
for phase in ['before','after']:
    h=hivex.Hivex(str(out/'artifacts'/(phase+'-system')));node=h.node_get_child(h.root(),'MountedDevices');assert node
    values={h.value_key(v):h.value_value(v)[1] for v in h.node_values(node)}
    maps[phase]=values['\\DosDevices\\C:'].hex();del h
expected=struct.pack('<IQ',0xaa55,5633024*512).hex();r['windows_C_binding']=maps
r['persisted_E_binding']=maps['before']==maps['after']==expected
r['scoped_second_boot_passed']=a['scoped_combined_passed']
r['strict_second_boot_passed']=a['strict_qualification_passed']
r['passed']=r['persisted_E_binding'] and r['no_extended_partition_table'] and r['no_F_filesystem'] and all(x['matched'] for x in r['files']) and not p['registry_edited'] and a['scoped_combined_passed']
r['limits']='Repeat-boot and file persistence scope only; known strict event failure is retained, no physical deployment/release qualification.'
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','persisted_E_binding','strict_second_boot_passed']}))
