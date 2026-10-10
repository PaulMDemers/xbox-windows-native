"""Create a fresh child of the closed, normally restarted emu001 disk."""
import hashlib,importlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1]
run=repo/'work/runs/nt5xidrestart-emu002';parent=repo/'work/runs/nt5xidrestart-emu001'
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def filehash(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not run.exists() and (parent/'cleanup.json').exists()
assert read(k/'emu001/restart-review.json')['scoped_restart_passed']
parenthash=filehash(parent/'hdd.qcow2');stage=read(parent/'stage.json')
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof'),str(canon/'outputs/device-observation188')]
from coldio import ColdIO
from allocation import scan
from restore import restore
m=importlib.import_module('prepare-fixture');disk=run/'hdd.qcow2';m.target=disk;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
def readers(io):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
run.mkdir()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../nt5xidrestart-emu001/hdd.qcow2',str(disk)],check=True)
fixture=read(k.parent/'usb-identification207/fixture-emu001.json')
with ColdIO(disk) as io:
    rr=readers(io)
    for name,digest in {**fixture['protected'],**stage['files']}.items():
        v,p=name.split('/',1);assert sha(rr[v].read(p))==digest,name
    assert sha(rr['F'].read('winnt/system32/drivers/xwnxid.sys'))==stage['build_files']['xwnxid.sys']
    for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
        data=rr['F'].read('winnt/system32/config/'+name)
        assert data==(parent/('after-'+name)).read_bytes(),name
        (run/('before-'+name)).write_bytes(data)
    data=rr['F'].read('winnt/setupapi.log');assert data==(parent/'after-setupapi.log').read_bytes()
    (run/'before-setupapi.log').write_bytes(data)
class OnlyF(m.SliceIO):
    def write(self,data):
        start,size=m.fatx.PARTITIONS['F'];assert start<=self.pos and self.pos+len(data)<=start+size
        return super().write(data)
io=OnlyF(disk);rr=readers(io);files=stage['files'].copy()
review=read(k/'verify001-review.json');assert review['passed']
data=(k/'artifacts/verify001/verify.exe').read_bytes();assert sha(data)==review['binary_sha256']
rr['F'].write('xwnxid/verify.exe',data);files['F/xwnxid/verify.exe']=sha(data)
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
command=b'@echo off\r\nC:\\xwnxid\\verify.exe\r\necho %errorlevel% > C:\\xwnxid\\exit-verify.txt\r\nexit\r\n'
restore(rr['F'],startup,command);files['F/'+startup]=sha(command);rr['F'].flush()
with ColdIO(disk) as io:
    rr=readers(io)
    for name,digest in {**fixture['protected'],**files}.items():
        v,p=name.split('/',1);assert sha(rr[v].read(p))==digest,name
scan(disk,k/'emu002/before/artifacts');a=read(k/'emu002/before/allocation.json')
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert filehash(parent/'hdd.qcow2')==parenthash
r=dict(physical_access=False,case='emu002',phase='verify',build=stage['build'],build_files=stage['build_files'],files=files,
    baseline_exact=True,allocation_passed=True,staged_disk_sha256=filehash(disk),parent_case='emu001',
    parent_closed_disk_sha256=parenthash,driver_reinstalled=False,wizard_actions_enabled=False)
(run/'stage.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS fresh subsequent-boot fixture, unchanged installed driver and parent')
