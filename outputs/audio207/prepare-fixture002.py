"""Fresh audio sibling: existing ACI binding, playback helpers and driver only."""
import json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/video-text-oracle206'))
from common import ColdIO,readers,sha,save,hive,scan,m,STARTUP,HIVES
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from restore import restore
case=sys.argv[1];assert case in ['candidate002'];out=k/case;out.mkdir(exist_ok=False)
art=out/'artifacts';art.mkdir()
original=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
f=json.loads((repo/'outputs/setup-wizard-automation201/fixture-observe002.json').read_text());base=pathlib.Path(f['fixture_path_linux'])
assert sha(base)==f['fixture_sha256']
root=repo.parent/'work/fixtures';root.mkdir(parents=True,exist_ok=True)
target=root/(case+'-preparation.qcow2');source=root/(case+'-source.qcow2');assert not target.exists() and not source.exists()
namespace='xwnaud207c'
external_sources={str(pathlib.Path(sys.modules[name].__file__).resolve()):sha(pathlib.Path(sys.modules[name].__file__).resolve()) for name in ['bulk_fatx','fatx_stage_boot']}
files=dict(f['files']);protected=dict(f['protected'])
inventory=json.loads((k/'inventory001.json').read_text())
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
    for name,digest in inventory['providers'].items():
        p='winnt/system32/'+('drivers/' if name.endswith('.sys') and name!='ntoskrnl.exe' else '')+name
        assert m.sha(rr['F'].read(p))==digest
        protected['F/'+p]=digest;files['F/'+p]=digest
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
sources={name:k/'artifacts/probe001'/name for name in ['runner.exe','probe.exe']}
sources['wizard.exe']=original/'outputs/setup-wizard-automation201/artifacts/build006/wizard.exe'
assert sha(sources['wizard.exe'])=='b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb'
for name,path in sources.items():
    p=namespace+'/'+name;rr['F'].write(p,path.read_bytes());files['F/'+p]=sha(path);protected['F/'+p]=sha(path)
if case=='candidate002':
    driver=k/'artifacts/build002/ac97xnt5.sys';p='winnt/system32/drivers/ac97xnt5.sys'
    restore(rr['F'],p,driver.read_bytes());files['F/'+p]=sha(driver);protected['F/'+p]=sha(driver)
startup=('@echo off\r\nC:\\'+namespace+'\\runner.exe\r\nexit\r\n').encode('ascii')
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
scan(source,out/'before/artifacts');a=json.loads((out/'before/allocation.json').read_text());assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
save(out/'fixture.json',dict(case=case,namespace=namespace,files=files,protected=protected,parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='E:'+str(source)[6:],fixture_sha256=sha(source),external_source_pins=external_sources,physical_access=False,registry_edits=False,guest_launch=False,limits='Existing emulator ACI binding. Known201 wizard cancellation is recorded separately; unsupported APU remains unsupported. No claim of installation or physical codec support.'))
print('Prepared and cold checked',case)
