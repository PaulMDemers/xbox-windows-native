"""Fresh standalone audio-installed child with physically exercised video118 and joined workloads."""
import json
import subprocess
import sys
from pathlib import Path

k=Path(__file__).resolve().parent; ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-text-oracle206'))
from common import ColdIO, readers, sha, save, hive, scan, m, STARTUP, HIVES
sys.path.insert(0,str(ws/'outputs/setup-wizard-automation201'))
from restore import restore
sys.path.insert(0,str(ws/'outputs/native-windows-nt5-kernel'))
from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex

peer=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo')
prior=peer/'outputs/audio-channel001'
assert json.loads((prior/'emu001/closure.json').read_text())['scoped_audio_passed']
f=json.loads((prior/'emu001/fixture.json').read_text())
base=Path(f['fixture_path_linux']); assert sha(base)==f['fixture_sha256']
out=k/'emu001';out.mkdir(exist_ok=False);art=out/'artifacts';art.mkdir()
root=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/demo251/fixtures')
root.mkdir(parents=True,exist_ok=False)
target=root/'combined001-preparation.qcow2';source=root/'combined001-source.qcow2'
namespace='xwndemo251'
files=dict(f['files']);protected=dict(f['protected'])
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():
        v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
    raw=rr['F'].read('winnt/system32/config/system')
    (art/'parent-system').write_bytes(raw)

def semantic(h):
    keys=set();values={};todo=[('',h.root())]
    while todo:
        path,n=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(n):values[path,h.value_key(v)]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values

p=art/'proposed-system';p.write_bytes(raw);h=hivex.Hivex(str(p),write=True)
keys,values=semantic(h);expected=dict(values)
current=int.from_bytes(values['\\Select','Current'][1],'little')
assert current==1, 'Review another active control set explicitly'
changes=json.loads((ws/'outputs/video-text-oracle206/binding-edit.json').read_text())['changes']
for row in changes:
    key=('\\'+row['path'],row['name'])
    assert values[key]==(row['type'],bytes.fromhex(row['before_hex']))
    n=h.root()
    for part in row['path'].split('\\'):
        n=h.node_get_child(n,part);assert n
    data=bytes.fromhex(row['after_hex'])
    h.node_set_value(n,dict(key=row['name'],t=row['type'],value=data))
    expected[key]=(row['type'],data)
h.commit(None);del h
data,indexes=normalize(p.read_bytes());p.write_bytes(data)
h=hivex.Hivex(str(p));assert semantic(h)==(keys,expected);del h
save(out/'binding-edit.json',dict(passed=True,changes=changes,only_two_expected_values_changed=True,
    parent_sha256=m.sha(raw),after_sha256=m.sha(data),indexes=indexes))
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
sources={
    'runner.exe':k/'artifacts/build001/runner.exe',
    'probe.exe':prior/'artifacts/build002/probe.exe',
    'state.exe':peer/'outputs/audio207/artifacts/state001/state.exe',
    'replay.exe':ws/'outputs/video-text-oracle206/artifacts/replay.exe',
    'wizard.exe':ws/'outputs/setup-wizard-automation201/artifacts/build006/wizard.exe'}
expected_helpers={'probe.exe':'5ddf733be56e5bbffbcf1ad69f69a6fe31584d4635683a37dd18a0b5c912db77',
    'replay.exe':'e7372a4585ddafd5a81a179befb13745a6588b2f17ed4d6d7bddde64af4b2ab9',
    'wizard.exe':'b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb',
    'state.exe':'7eaff4ef526c0d3a8c5b1c3af49fb318c2ea1d09889b5ac923669250c637a343',
    'runner.exe':json.loads((k/'runner-build001.json').read_text())['binary_sha256']}
for name,path in sources.items():
    assert sha(path)==expected_helpers[name],name
    p=namespace+'/'+name;rr['F'].write(p,path.read_bytes());files['F/'+p]=sha(path);protected['F/'+p]=sha(path)
payload=json.loads((ws/'outputs/video-text-oracle206/package-review.json').read_text())['cases']['candidate001']
for row in payload:
    blob=(ws/row['source']).read_bytes();assert m.sha(blob)==row['sha256']
    v,p=row['target'].split('/',1);restore(rr[v],p,blob)
    files[row['target']]=row['sha256'];protected[row['target']]=row['sha256']
restore(rr['F'],'winnt/system32/config/system',data);files['F/winnt/system32/config/system']=m.sha(data)
startup=('@echo off\r\nC:\\'+namespace+'\\runner.exe /emulator\r\nexit\r\n').encode('ascii')
restore(rr['F'],STARTUP,startup);files['F/'+STARTUP]=m.sha(startup)
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]));assert not info.get('backing-filename')
with ColdIO(source) as io:
    rr=readers(io,source)
    for name,digest in files.items():
        v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
    for name in HIVES:
        p=art/('before-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));hive(p)
scan(source,out/'before/artifacts');a=json.loads((out/'before/allocation.json').read_text())
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
save(out/'fixture.json',dict(prepared=True,namespace=namespace,files=files,protected=protected,
    parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_linux=str(source),
    fixture_path_windows='E:'+str(source)[6:],fixture_sha256=sha(source),helpers=expected_helpers,
    payload=payload,physical_access=False,guest_launch=False,inherited_null_policy=False,
    limits='Previously installed real ACI fixture plus exact physically tested118 display chain; new combined runtime unqualified.'))
print('Combined standalone fixture prepared and cold checked')
