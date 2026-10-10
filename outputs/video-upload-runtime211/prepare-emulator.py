"""Fresh standalone202 siblings from immutable physical-core201 prelaunch, no physical writes."""
import subprocess
from common import *
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'))
from restore import restore
sys.path.insert(0,str(k.parent/'native-windows-nt5-kernel'))
from nt5_hive_indexes import normalize
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex

case=sys.argv[1];assert case in ['control001','candidate001'];out=k/('emu-'+case);out.mkdir(exist_ok=False)
assert read(k/'build-review.json')['passed'] and read(k.parent/'setup-wizard-automation201/physical001/review.json')['passed']
f=read(k.parent/'setup-wizard-automation201/fixture-observe002.json');base=Path(f['fixture_path_linux'])
assert sha(base)==f['fixture_sha256']
root=Path('/mnt/e/Codex-archive/xbox-windows-native/upload211');root.mkdir(exist_ok=True)
target=root/(case+'-preparation.qcow2');source=root/(case+'-source.qcow2');assert not target.exists() and not source.exists()
namespace='xwnua211a' if case=='control001' else 'xwnua211b'
files=dict(f['files']);protected=dict(f['protected']);art=out/'artifacts';art.mkdir()
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
    for dll,row in read(k/'build-review.json')['providers'].items():
        p='winnt/system32/'+dll;assert m.sha(rr['F'].read(p))==row['sha256'];protected['F/'+p]=row['sha256']
    system=rr['F'].read('winnt/system32/config/system');(art/'before-system').write_bytes(system)

def semantic(h):
    keys=set();values={};todo=[('',h.root())]
    while todo:
        path,n=todo.pop();assert path not in keys;keys.add(path)
        for v in h.node_values(n):values[path,h.value_key(v)]=h.value_value(v)
        todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
    return keys,values
path=art/'proposed-system';path.write_bytes(system);h=hivex.Hivex(str(path),write=True)
keys,values=semantic(h);expected=dict(values)
changes=read(k.parent/'video-phase-physical200/binding-edit.json')['changes']
for row in changes:
    n=h.root()
    for part in row['path'].split('\\'):n=h.node_get_child(n,part);assert n
    key=('\\'+row['path'],row['name']);assert values[key]==(row['type'],bytes.fromhex(row['before_hex']))
    h.node_set_value(n,dict(key=row['name'],t=row['type'],value=bytes.fromhex(row['after_hex'])))
    expected[key]=(row['type'],bytes.fromhex(row['after_hex']))
h.commit(None);del h
data,indexes=normalize(path.read_bytes());path.write_bytes(data);h=hivex.Hivex(str(path))
assert semantic(h)==(keys,expected);del h
save(out/'binding-edit.json',dict(passed=True,before_sha256=m.sha(system),after_sha256=m.sha(data),changes=changes,indexes=indexes,only_two_expected_values_changed=True))
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
for name in ['runner.exe','replay.exe','wizard.exe']:
    p=namespace+'/'+name;rr['F'].write(p,(k/'artifacts'/name).read_bytes());files['F/'+p]=sha(k/'artifacts'/name);protected['F/'+p]=files['F/'+p]
payloads=read(k.parent/'video-phase-physical200/package-review.json')['cases'][case]
payloads=[dict(row,source=str((k.parent/'video-upload-accounting210'/case/'artifacts/xwnown.dll').relative_to(ws)),sha256=sha(k.parent/'video-upload-accounting210'/case/'artifacts/xwnown.dll')) if row['target'].endswith('/xwnown.dll') else row for row in payloads]
for row in payloads:
    v,p=row['target'].split('/',1);blob=(ws/row['source']).read_bytes();assert m.sha(blob)==row['sha256']
    restore(rr[v],p,blob);files[row['target']]=row['sha256'];protected[row['target']]=row['sha256']
restore(rr['F'],'winnt/system32/config/system',data);files['F/winnt/system32/config/system']=m.sha(data)
startup=('@echo off\r\nC:\\'+namespace+'\\runner.exe /emulator\r\nexit\r\n').encode('ascii')
restore(rr['F'],STARTUP,startup);files['F/'+STARTUP]=m.sha(startup)
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]));assert not info.get('backing-filename')
with ColdIO(source) as io:
    after=readers(io,source)
    for name,digest in files.items():v,p=name.split('/',1);assert m.sha(after[v].read(p))==digest,name
    for name in HIVES:
        p=art/('before-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name));hive(p)
scan(source,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,prepared=True,namespace=namespace,files=files,protected=protected,
 parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/upload211/'+source.name,
 fixture_sha256=sha(source),seed_sha256=sha(source),physical_access=False,guest_launch=False,
 inherited_null_policy=False,device_policy='Captured physical core, including known unsupported queue. No synthetic null device binding.',
 limits='Only reviewed shared display providers/profile OFF or ON, two display tokens and new helpers/startup. Fresh cold-integrity validation required. No physical or timing qualification.'))
print('Fresh202 standalone prepared/full cold checked:',case)
