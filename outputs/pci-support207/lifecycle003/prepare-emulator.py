"""Fresh genuine PnP resource-only installation; no physical access or bus transactions."""
import json,os,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[2]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert (repo/'.git/HEAD').read_text().strip()=='ref: refs/heads/codex/xbox-native-pci'
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from common import ColdIO,readers,read,save,sha,hive,scan,m,STARTUP
from restore import restore
canonical=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
manifest=read(canonical/'outputs/setup-wizard-automation201/fixture-observe002.json')
assert read(k/'build-review001.json')['passed']
base=Path(manifest['fixture_path_linux']);assert sha(base)==manifest['fixture_sha256']
out=k/'emulator001';assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
source=art/'source.qcow2';files=dict(manifest['files'])
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():
        volume,path=name.split('/',1);assert m.sha(rr[volume].read(path))==digest,name
shutil.copyfile(base,source);assert sha(source)==manifest['fixture_sha256']
m.target=source;io=m.SliceIO(source);w=m.Writer(io,m.fatx.open_partition(io,source,'F'))
for name in ('xwnrsc.sys','install.exe','probe.exe','xwnrsc.inf'):
    data=((k/name) if name.endswith('.inf') else (k/'artifacts/build001'/name)).read_bytes()
    expected=next(v['sha256'] for v in (read(k/'build001.json')['files']+read(k/'build001.json')['sources']) if v['name']==name);assert m.sha(data)==expected
    w.write('xwnpcilife3/'+name,data);files['F/xwnpcilife3/'+name]=m.sha(data)
data=b'@echo off\r\nC:\\xwnpcilife3\\install.exe\r\n>C:\\xwnpcilife3\\install-exit.txt echo INSTALL_EXIT %errorlevel%\r\nC:\\xwnpcilife3\\probe.exe\r\n>C:\\xwnpcilife3\\probe-exit.txt echo PROBE_EXIT %errorlevel%\r\nexit\r\n'
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
save(out/'fixture.json',dict(scope=__doc__,physical_access=False,base=str(base),base_sha256=manifest['fixture_sha256'],source_sha256=sha(source),standalone=True,files=files,hives=hives,no_registry_edits=True,resource_only_driver_installation=True))
print('lifecycle003 emulator001 prepared; no console access')
