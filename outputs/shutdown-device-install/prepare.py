"""Stage a real GPU package using unchanged video0093 and the installed framebuf DLL."""
import importlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
r=json.loads((k.parent/'shutdown-popup-workload/fixture-001.json').read_text())
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name']
parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name('shutdown-device-install-001.qcow2');seed=ws/'work/shutdown-device-install-001-seed.qcow2'
assert not target.exists() and not seed.exists() and shutil.disk_usage('/mnt/c').free>8*1024**3
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
system=w.read('winnt/system32/config/system');startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
startup_bytes=w.read(startup)
for row in r['payloads']+r['preserved_payloads']:
    assert m.sha(w.read(row['path']))==row['sha256']
binary=w.read('winnt/system32/drivers/xboxvnt5.sys')
assert m.sha(binary)=='3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'
inf=(k/'xwnvideo.inf').read_bytes()
for path,data in [('xwninf99/xwnvideo.inf',inf),('xwninf99/xboxvnt5.sys',binary)]:r['payloads'].append(w.write(path,data))
out=k/'001/artifacts';out.mkdir(parents=True,exist_ok=True)
raw=w.read('winnt/system32/config/software');before=out/'before-software';before.write_bytes(raw)
def node(h,path):
    n=h.root()
    for part in path.split('\\'):n=h.node_get_child(n,part);assert n,path
    return n
def semantic(h):
    keys=set();values={};pending=[('',h.root())]
    while pending:
        path,n=pending.pop();keys.add(path)
        for v in h.node_values(n):values[(path,h.value_key(v))]=h.value_value(v)
        pending.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values
h=hivex.Hivex(str(before));keys,values=semantic(h);path=r'Microsoft\Windows\CurrentVersion'
old=h.value_string(h.node_get_value(node(h,path),'DevicePath'));new=old+';C:\\xwninf99'
assert 'xwninf99' not in old.lower()
edit=out/'edited-software';edit.write_bytes(raw);h=hivex.Hivex(str(edit),write=True)
value=new.encode('utf-16le')+b'\0\0';h.node_set_value(node(h,path),{'key':'DevicePath','t':2,'value':value});h.commit(None);del h
data,indexes=normalize(edit.read_bytes());edit.write_bytes(data);h=hivex.Hivex(str(edit));newkeys,newvalues=semantic(h)
expected=dict(values);expected[('\\'+path,'DevicePath')]=(2,value)
assert keys==newkeys and expected==newvalues
m.replace(w,'winnt/system32/config/software',data);w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in r['payloads']+r['preserved_payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert fresh.read('winnt/system32/config/software')==data
assert fresh.read('winnt/system32/config/system')==system and fresh.read(startup)==startup_bytes
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,parent_fixture_sha256=parent_hash,fixture_name=target.name,
    fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
    software_edit=dict(path=path,value='DevicePath',before=old,after=new,all_keys_checked=len(keys),all_values_checked=len(values),only_expected_value_changed=True,index_normalization=indexes),
    software_before_sha256=m.sha(raw),software_after_sha256=m.sha(data),
    system_unchanged_during_staging=True,startup_unchanged=True,
    installation_method='Normal PnP discovery via DevicePath; existing framebuf DLL referenced but not copied.',
    limits='Owned emulator only. Same exact rehearsal workload and baseline binaries. No signing-policy change, forced installation or new FAILEDINSTALL flags. Inherited fixture limitations remain.')
(k/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n');print('Package fixture and single SOFTWARE change verified')
