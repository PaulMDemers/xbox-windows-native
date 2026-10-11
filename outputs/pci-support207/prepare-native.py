"""Fresh isolated NT5 install fixture: staged real package, no registry binding edits."""
import hashlib,importlib,json,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1]
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert (repo/'.git/HEAD').read_text().strip()=='ref: refs/heads/codex/xbox-native-pci'
assert subprocess.check_output(['git','-C',str(repo),'remote','get-url','origin'],text=True).strip()=='https://github.com/PaulMDemers/xbox-windows-native.git'
canonical=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,str(repo/'outputs/setup-wizard-automation201'))
from restore import restore
sys.path.insert(0,str(repo/'outputs/fatx-mapped-eof'))
from coldio import ColdIO
from allocation import scan
sys.path.insert(0,str(repo/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
sys.path.insert(0,str(k));from inventory import snapshot
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,data):p.write_text(json.dumps(data,indent=2)+'\n')
build=read(k/'driver004-build.json');assert read(k/'driver004-review.json')['passed']
assert read(k/'driver003-constraint-tests.json')['passed']
assert all(read(k/(case+'.json'))['passed'] and read(k/(case+'.json'))['closed'] for case in ('model003','model004'))
for row in build['sources']:assert sha(k/row['name'])==row['sha256']
for row in build['files']:assert sha(k/'artifacts/driver004'/row['name'])==row['sha256']
f=read(canonical/'outputs/setup-wizard-automation201/fixture-observe002.json')
seed=Path(f['fixture_path_linux']);assert sha(seed)==f['fixture_sha256']
info=read(canonical/'outputs/setup-wizard-automation201/observe002/closure.json');assert info['closed']
out=k/'native001';assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
target=art/'staged.qcow2';source=art/'source.qcow2';files=dict(f['files'])
with ColdIO(seed) as io:
    rr={v:m.Writer(io,m.fatx.open_partition(io,seed,v)) for v in ('E','F')}
    for name,digest in files.items():
        v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(seed),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for name in ('xwnsmb.sys','xwnsmb.inf','install.exe','probe.exe'):
    path='xwnpci207/'+name;data=(k/'artifacts/driver004'/name).read_bytes()
    try:w.read(path)
    except KeyError:pass
    else:raise AssertionError('Stage path already exists')
    w.write(path,data);files['F/'+path]=m.sha(data)
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
data=b'@echo off\r\nC:\\xwnpci207\\install.exe\r\nC:\\xwnpci207\\probe.exe\r\nexit\r\n'
restore(w,startup,data);files['F/'+startup]=m.sha(data);w.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)])).get('backing-filename')
hives=[]
with ColdIO(source) as io:
    rr={v:m.Writer(io,m.fatx.open_partition(io,source,v)) for v in ('E','F')}
    for name,digest in files.items():
        v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
    for name in ('system','software','default','sam','security'):
        p=art/('before-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));values=snapshot(p)
        hives.append({'name':name,'sha256':sha(p),'keys':len(values)})
scan(source,art/'before');allocation=read(art/'allocation.json')
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
assert sha(seed)==f['fixture_sha256']
save(out/'fixture.json',{'scope':__doc__,'physical_access':False,'guest_launched':False,
     'seed':str(seed),'seed_sha256':sha(seed),'source':str(source),'source_sha256':sha(source),
     'standalone':True,'virtual_compare_equal':True,'files':files,'hives':hives,
     'driver_build_sha256':sha(k/'driver004-build.json'),'no_registry_edits':True,
     'limits':'Installation/runtime not tested. No helper201 or dialog cancellation. Unknown audio/modem/USB prompts remain unresolved.'})
print('native001 prepared; no guest launch')
