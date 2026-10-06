"""Diagnostic only: restore system-start in a child of the pre-reboot installed state."""
import importlib,json,shutil,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/native-windows-nt5-kernel'));from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-nt5-display-package-004.qcow2'
r=json.loads((k/'fixture-004.json').read_text());parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name('video-nt5-display-package-005.qcow2');seed=ws/'work/video-nt5-display-package-005-seed.qcow2'
assert not target.exists() and not seed.exists() and shutil.disk_usage('/mnt/c').free>8*1024**3
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
out=k/'005/artifacts';out.mkdir(parents=True,exist_ok=True)
raw=w.read('winnt/system32/config/system');before=out/'before-system';before.write_bytes(raw)
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
h=hivex.Hivex(str(before));keys,values=semantic(h)
current=h.value_dword(h.node_get_value(node(h,'Select'),'Current'));path='ControlSet%03d\\Services\\XboxVnt5'%current
old=h.value_dword(h.node_get_value(node(h,path),'Start'));assert old==3
edit=out/'edited-system';edit.write_bytes(raw);h=hivex.Hivex(str(edit),write=True)
value=struct.pack('<I',1);h.node_set_value(node(h,path),{'key':'Start','t':4,'value':value});h.commit(None);del h
data,indexes=normalize(edit.read_bytes());edit.write_bytes(data);h=hivex.Hivex(str(edit));newkeys,newvalues=semantic(h)
expected=dict(values);expected[('\\'+path,'Start')]=(4,value);assert keys==newkeys and expected==newvalues
m.replace(w,'winnt/system32/config/system',data);w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'));assert fresh.read('winnt/system32/config/system')==data
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,parent_fixture_sha256=parent_hash,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         guest_file_edits=True,system_unchanged_during_staging=False,registry_hives_unchanged_during_staging=False,
         system_start_diagnostic=dict(path=path,value='Start',before=old,after=1,all_keys_checked=len(keys),all_values_checked=len(values),only_expected_value_changed=True,index_normalization=indexes),
         system_before_sha256=m.sha(raw),system_after_sha256=m.sha(data),installation_method='One-value offline diagnostic; not a corrected INF installation recipe')
(k/'fixture-005.json').write_text(json.dumps(r,indent=2)+'\n');print('One-value system-start diagnostic verified')
