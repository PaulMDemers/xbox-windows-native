"""Fresh genuine PnP resource-only installation; no physical access or bus transactions."""
import json,os,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent
variant=sys.argv[1];assert variant in ('control','candidate')
k=k;repo=k.parents[2]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert (repo/'.git/HEAD').read_text().strip()=='ref: refs/heads/codex/xbox-native-pci'
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO,readers,read,save,sha,hive,scan,m,STARTUP
from restore import restore
from e_allocation import scan_e
canonical=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
manifest=read(canonical/'outputs/setup-wizard-automation201/fixture-observe002.json')
assert read(k/'build-review001.json')['passed']
base=Path(manifest['fixture_path_linux']);assert sha(base)==manifest['fixture_sha256']
out=k/(variant+'001');assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
source=art/'source.qcow2';files=dict(manifest['files'])
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():
        volume,path=name.split('/',1);assert m.sha(rr[volume].read(path))==digest,name
shutil.copyfile(base,source);assert sha(source)==manifest['fixture_sha256']
hal_record=read(k.parent/'handoff001/build001.json')
hal_path=k.parent/('handoff001/artifacts/build001/native/artifacts/halxboxnt5.dll' if variant=='control' else 'handoff001/artifacts/build001/halxboxnt5.dll')
hal_digest=next(x['sha256'] for x in hal_record['baseline']['artifacts'] if x['name']=='halxboxnt5.dll') if variant=='control' else hal_record['candidate_sha256']
assert sha(hal_path)==hal_digest
e_before=scan_e(source,art/'e-before.json')
m.target=source;io=m.SliceIO(source);ew=m.Writer(io,m.fatx.open_partition(io,source,'E'))
io.seek(ew.p.partition_offset);e_meta=io.read(ew.p.cluster1_offset-ew.p.partition_offset)
e_restore=restore(ew,'Applications/XWNFBoot/loader/halxboxnt5.dll',hal_path.read_bytes())
ew.flush()
e_after=scan_e(source,art/'e-prepared.json')
io.seek(ew.p.partition_offset);e_meta=io.read(len(e_meta))
e_metadata=dict(offset=ew.p.partition_offset,size=len(e_meta),sha256=m.sha(e_meta),allocation_unchanged=e_before['metadata_sha256']==e_after['metadata_sha256'],restore_method=e_restore)
files['E/Applications/XWNFBoot/loader/halxboxnt5.dll']=hal_digest
m.target=source;io=m.SliceIO(source);w=m.Writer(io,m.fatx.open_partition(io,source,'F'))
for name in ('xwnrsc.sys','install.exe','probe.exe','xwnrsc.inf'):
    data=((k/name) if name.endswith('.inf') else (k/'artifacts/build001'/name)).read_bytes()
    expected=next(v['sha256'] for v in (read(k/'build001.json')['files']+read(k/'build001.json')['sources']) if v['name']==name);assert m.sha(data)==expected
    w.write('xwnpcican1/'+name,data);files['F/xwnpcican1/'+name]=m.sha(data)
data=b'@echo off\r\nC:\\xwnpcican1\\install.exe\r\n>C:\\xwnpcican1\\install-exit.txt echo INSTALL_EXIT %errorlevel%\r\nC:\\xwnpcican1\\probe.exe\r\n>C:\\xwnpcican1\\probe-exit.txt echo PROBE_EXIT %errorlevel%\r\nexit\r\n'
data=data.replace(b'@echo off\r\n',b'@echo off\r\nset XWN_HAL_EXPECT='+ (b'0' if variant=='control' else b'1') +b'\r\n')
(art/'startup.cmd').write_bytes(data);restore(w,STARTUP,data);files['F/'+STARTUP]=m.sha(data);w.flush()
hives=[]
with ColdIO(source) as io:
    rr=readers(io,source)
    for name,digest in files.items():
        volume,path=name.split('/',1);assert m.sha(rr[volume].read(path))==digest,name
    for name in ('system','software','default','sam','security'):
        p=art/('before-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));hives.append(dict(name=name,**hive(p)))
scan(source,art/'before');allocation=read(art/'allocation.json')
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
assert sha(base)==manifest['fixture_sha256']
save(out/'fixture.json',dict(scope=__doc__,physical_access=False,base=str(base),base_sha256=manifest['fixture_sha256'],source_sha256=sha(source),standalone=True,files=files,hives=hives,no_registry_edits=True,resource_only_driver_installation=True,e_metadata=e_metadata,e_before=e_before,e_prepared=e_after,hal_variant=variant,hal_sha256=hal_digest,hal_build_record_sha256=sha(k.parent/'handoff001/build001.json')))
print('cancel001 emulator001 prepared; no console access')
