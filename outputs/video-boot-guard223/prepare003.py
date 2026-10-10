"""Unique ordinary222 standalone child; exact helpers/policy, no physical IO."""
import subprocess
from common import *
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'));from restore import restore
case=sys.argv[1];assert case in ['control003','candidate003'];out=k/case;assert not out.exists();provider_case=case.replace('003','001')
review=read(k.parent/'video-resident-context222/build-review005.json');assert review['passed']
f=read(k.parent/'video-upload-runtime211/fixture-candidate001.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
root=Path('/mnt/e/Codex-archive/xbox-windows-native/bootguard223');root.mkdir(exist_ok=True)
target=root/(case+'-preparation.qcow2');source=root/(case+'-source.qcow2');assert not target.exists() and not source.exists()
out.mkdir();art=out/'artifacts';art.mkdir();files=dict(f['files']);protected=dict(f['protected'])
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
for name in ['probe.exe','resident.sys','wizard.exe','result.log','wizard201.log']:
    try:rr['F'].read('xwnctx222/'+name)
    except KeyError:pass
    else:raise AssertionError('Namespace not fresh')
for name in ['probe.exe','resident.sys','wizard.exe']:
    if name=='wizard.exe':
        p=k.parent/'video-upload-runtime211/artifacts'/name;expected=read(k.parent/'video-upload-runtime211/build-review.json')['binaries'][name]['sha256']
    else:p=k.parent/'video-resident-context222/artifacts/build005'/name;expected=review['binaries'][name]['sha256']
    assert sha(p)==expected;rr['F'].write('xwnctx222/'+name,p.read_bytes());files['F/xwnctx222/'+name]=expected;protected['F/xwnctx222/'+name]=expected
p=k.parent/'video-boot-layout219/artifacts/build001'/provider_case/'xboxbvid.dll'
expected=read(k.parent/'video-boot-layout219/build-review.json')['binaries'][provider_case]['sha256'];assert sha(p)==expected
path='Applications/XWNFBoot/loader/xboxbvid.dll';restore(rr['E'],path,p.read_bytes());files['E/'+path]=expected;protected['E/'+path]=expected
startup=b'@echo off\r\nC:\\xwnctx222\\wizard.exe /cancel-emulator\r\nif errorlevel 1 exit /b 95\r\nC:\\xwnctx222\\probe.exe\r\nexit\r\n'
restore(rr['F'],STARTUP,startup);files['F/'+STARTUP]=m.sha(startup)
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)])).get('backing-filename')
with ColdIO(source) as cold:
    after=readers(cold,source)
    for name,digest in files.items():v,p=name.split('/',1);assert m.sha(after[v].read(p))==digest,name
    for name in HIVES:
        p=art/('before-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name));hive(p)
scan(source,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,prepared=True,namespace='xwnctx222',files=files,protected=protected,parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/bootguard223/'+source.name,fixture_sha256=sha(source),seed_sha256=sha(source),physical_access=False,guest_launch=False,device_policy=f['device_policy'],inherited_null_policy=False,debugger=False,gpu_access=False,ordinary_qualified=False))
print('Fresh223 '+case+' prepared and cold audited')
