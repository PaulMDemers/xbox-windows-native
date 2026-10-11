"""Fresh audio sibling: existing ACI binding, playback helpers and driver only."""
import json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,str(repo/'outputs/video-text-oracle206'))
from common import ColdIO,readers,sha,save,hive,scan,m,STARTUP,HIVES
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from restore import restore
case=sys.argv[1];assert case in ['installed002'];out=k/case;out.mkdir(exist_ok=False)
art=out/'artifacts';art.mkdir()
original=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
installation=json.loads((k/'install001/audit.json').read_text())
assert installation['scoped_installation_passed']
assert json.loads((k/'install001/closure.json').read_text())['closed']
assert json.loads((k/'installed001/audit.json').read_text())['scoped_audio_passed']
assert json.loads((k/'installed001/closure.json').read_text())['closed']
f=json.loads((k/'installed001/fixture.json').read_text())
base=repo/'work/runs/nt5-audio207-installed001/hdd.qcow2'
parent_sha=sha(base)
root=repo.parent/'work/fixtures';root.mkdir(parents=True,exist_ok=True)
target=root/(case+'-preparation.qcow2');source=root/(case+'-source.qcow2');assert not target.exists() and not source.exists()
namespace='xwnpost207b'
external_sources={str(pathlib.Path(sys.modules[name].__file__).resolve()):sha(pathlib.Path(sys.modules[name].__file__).resolve()) for name in ['bulk_fatx','fatx_stage_boot']}
files={};protected={}
with ColdIO(base) as io:
    rr=readers(io,base)
    # Capture installed parent bytes, including its genuine registry/event history.
    for name in set(f['files'])|set(f['protected']):
        v,p=name.split('/',1);digest=m.sha(rr[v].read(p));files[name]=digest
        if name in f['protected']:protected[name]=digest
    inf=installation['installed_binding']['driver_class']['infpath'][0]
    assert '/' not in inf and chr(92) not in inf and '..' not in inf
    for p in ['winnt/system32/drivers/xwnaci207.sys','winnt/inf/'+inf,'winnt/system32/psapi.dll']:
        digest=m.sha(rr['F'].read(p));files['F/'+p]=digest;protected['F/'+p]=digest
    assert protected['F/winnt/system32/drivers/xwnaci207.sys']==sha(k/'artifacts/build004/ac97xnt5.sys')
    assert protected['F/winnt/inf/'+inf]==sha(k/'xwnaci207.inf')
    assert protected['F/winnt/system32/psapi.dll']==json.loads((k/'state-provider001.json').read_text())['providers']['psapi.dll']
    for name in ['audio207.log','runner207.log','wizard201.log','state207.log']:
        p=f['namespace']+'/'+name;digest=m.sha(rr['F'].read(p))
        files['F/'+p]=digest;protected['F/'+p]=digest
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
sources={'runner.exe':k/'artifacts/state001/installed-runner.exe','probe.exe':k/'artifacts/state001/probe-installed.exe','state.exe':k/'artifacts/state001/state.exe'}
sources['wizard.exe']=original/'outputs/setup-wizard-automation201/artifacts/build006/wizard.exe'
assert sha(sources['wizard.exe'])=='b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb'
for name,path in sources.items():
    p=namespace+'/'+name;rr['F'].write(p,path.read_bytes());files['F/'+p]=sha(path);protected['F/'+p]=sha(path)
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
assert sha(base)==parent_sha
save(out/'fixture.json',dict(case=case,namespace=namespace,files=files,protected=protected,parent=str(base),parent_sha256=parent_sha,fixture_path_linux=str(source),fixture_path_windows='E:'+str(source)[6:],fixture_sha256=sha(source),external_source_pins=external_sources,physical_access=False,registry_edits=False,guest_launch=False,limits='Subsequent cold boot from genuinely installed and audited parent. Only new helper namespace and startup changed; no driver, INF or registry edits/reinstall. Known201 handles unrelated prompts, never ACI.'))
print('Prepared and cold checked',case)
