"""Prepare a one-device failed-install experiment and unchanged control in owned overlays."""
import importlib,json,shutil,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/native-windows-nt5-kernel'))
from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-surface-lifecycle-002.qcow2'
original=json.loads((ws/'outputs/video-surface-lifecycle/fixture.json').read_text())
assert m.filehash(parent)==original['fixture_sha256']
assert shutil.disk_usage('/mnt/c').free>8*1024**3
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
device=r'PCI\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1\2&ebb567f&0&28'
def node(h,path):
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part);assert n,path
 return n
def semantic(h):
 values={};keys=set();pending=[('',h.root())]
 while pending:
  path,n=pending.pop();assert path not in keys;keys.add(path)
  for v in h.node_values(n):
   t,d=h.value_value(v);values[(path,h.value_key(v))]=(t,d)
  pending.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
 return keys,values
for name,changed in [('audio003',True),('control003',False)]:
 out=k/name;out.mkdir(exist_ok=True);art=out/'artifacts';art.mkdir(exist_ok=True)
 target=parent.with_name('video-installer-'+name+'.qcow2');seed=ws/('work/video-installer-'+name+'-seed.qcow2')
 assert not target.exists() and not seed.exists() and not (out/'fixture.json').exists()
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
 m.target=target
 io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
 raw=w.read('winnt/system32/config/system');before=art/'before-system';before.write_bytes(raw)
 h=hivex.Hivex(str(before));keys,values=semantic(h)
 current=h.value_dword(h.node_get_value(node(h,'Select'),'Current'))
 path='ControlSet%03d\\Enum\\'%current+device;n=node(h,path)
 names={h.value_key(v) for v in h.node_values(n)}
 assert not names.intersection({'Driver','Service','ConfigFlags'})
 edit=dict(scope='One active-control-set device ConfigFlags only; no service disable or driver installation',device=device,path=path,before=None,after=64 if changed else None,changed=changed)
 if changed:
  work=art/'edited-system';work.write_bytes(raw);h=hivex.Hivex(str(work),write=True)
  h.node_set_value(node(h,path),{'key':'ConfigFlags','t':4,'value':struct.pack('<I',0x40)})
  h.commit(None);del h
  data,indexes=normalize(work.read_bytes());work.write_bytes(data)
  h=hivex.Hivex(str(work));newkeys,newvalues=semantic(h)
  expected=dict(values);expected[('\\'+path,'ConfigFlags')]=(4,struct.pack('<I',0x40))
  assert newkeys==keys and newvalues==expected
  edit.update(all_keys_checked=len(keys),all_values_checked=len(values),only_expected_value_changed=True,index_normalization=indexes)
  m.replace(w,'winnt/system32/config/system',data);w.flush()
  fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'));assert fresh.read('winnt/system32/config/system')==data
 else:data=raw
 for row in original['payloads']:assert m.sha(w.read(row['path']))==row['sha256']
 assert m.sha(w.read('winnt/system32/drivers/xwnfatx.sys'))==original['fatx_sha256']
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
 r=dict(original);r.update(scope=__doc__,parent_fixture_sha256=original['fixture_sha256'],fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),system_before_sha256=m.sha(raw),system_after_sha256=m.sha(data),registry_edit=edit)
 (out/'fixture.json').write_text(json.dumps(r,indent=2)+'\n')
assert m.filehash(parent)==original['fixture_sha256']
print('Two isolated fixtures verified; only audio003 changes one ConfigFlags value')
