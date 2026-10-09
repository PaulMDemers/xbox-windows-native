"""Prepare a private standalone descriptor-observer fixture; no policy/driver change."""
import hashlib,importlib,json,os,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1]
canonical=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
assert (repo/'.git/HEAD').read_text().strip()=='ref: refs/heads/codex/xbox-native-usb'
assert subprocess.check_output(['git','-C',str(repo),'config','--get','remote.origin.url'],text=True).strip()=='https://github.com/PaulMDemers/xbox-windows-native.git'
sys.path[:0]=[str(canonical/'outputs/fatx-mapped-eof'),str(canonical/'outputs/native-windows-paint-save'),str(canonical/'outputs/device-observation188')]
from coldio import ColdIO
from allocation import scan
from restore import restore
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
read=lambda p:json.loads(p.read_text())
for name,digest in read(k/'helper-pins.json').items():assert sha(canonical/name)==digest,name
build=read(k/'build-review.json');assert build['passed']
binary=k/build['binary'];assert sha(binary)==build['binary_sha256']
f=read(canonical/'outputs/setup-wizard-automation201/fixture-observe002.json');base=Path(f['fixture_path_linux'])
assert sha(base)==f['fixture_sha256']
out=k/'artifacts/emu001';out.mkdir(parents=True,exist_ok=False)
target=out/'preparation.qcow2';seed=out/'seed.qcow2'
files=dict(f['files']);protected=dict(f['protected']);providers={}
def readers(io,disk):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
    for name,row in build['providers'].items():
        p='winnt/system32/'+name;assert m.sha(rr['F'].read(p))==row['sha256'],name;protected['F/'+p]=row['sha256']
    for name in ['openhci.sys','usbd.sys','usbhub.sys','hidusb.sys','hidclass.sys','hidparse.sys','kbdhid.sys','mouhid.sys']:
        p='winnt/system32/drivers/'+name;b=rr['F'].read(p);providers[name]=m.sha(b);protected['F/'+p]=m.sha(b)
    for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
        (out/('before-'+name)).write_bytes(rr['F'].read('winnt/system32/config/'+name))
    (out/'before-setupapi.log').write_bytes(rr['F'].read('winnt/setupapi.log'))
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
rr['F'].write('xwnusb207/usbprobe.exe',binary.read_bytes());files['F/xwnusb207/usbprobe.exe']=sha(binary)
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
command=b'@echo off\r\nC:\\xwnusb207\\usbprobe.exe\r\nexit\r\n'
restore(rr['F'],startup,command);files['F/'+startup]=m.sha(command)
for w in rr.values():w.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(seed)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(seed)]));assert not info.get('backing-filename')
with ColdIO(seed) as io:
    rr=readers(io,seed)
    for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
scan(seed,k/'emu001/before/artifacts');a=read(k/'emu001/before/allocation.json')
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
r=dict(prepared=True,parent=str(base),parent_sha256=f['fixture_sha256'],seed_sha256=sha(seed),files=files,protected=protected,usb_providers=providers,
 source_sha256=sha(Path(__file__)),physical_access=False,guest_launch=False,device_policy_unchanged=True,cancellation_helper=False,
 limits='Captured physical registry/core, emulated USB hardware. Read-only topology collection; host bounded stop if no manual normal restart. Not persistence, input, or physical gamepad qualification.')
(k/'fixture-emu001.json').write_text(json.dumps(r,indent=2)+'\n');print('Prepared standalone USB207 seed with byte readback and cold allocation checks')
