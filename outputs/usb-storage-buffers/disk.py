"""Scoped private fixture preparation/collection; never physical FTP or repair."""
import hashlib,importlib,json,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1];mode,case=sys.argv[1:]
assert mode in ['stage','audit'] and case in ['emu001','emu002']
phase=2;run=repo/('work/runs/nt5storbuf-'+case);disk=run/'hdd.qcow2'
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof'),str(canon/'outputs/device-observation188')]
from coldio import ColdIO
from allocation import scan
from restore import restore
m=importlib.import_module('prepare-fixture');m.target=disk;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
def filehash(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def readers(io):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
def missing(w,path):
    try:w.read(path)
    except KeyError:return True
    return False
def capture(rr,label):
    hives={}
    for n in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
        data=rr['F'].read('winnt/system32/config/'+n);(run/(label+'-'+n)).write_bytes(data)
        if n.endswith('.evt'):continue
        a,b=struct.unpack_from('<II',data,4);cs=0
        for at in range(0,508,4):cs^=struct.unpack_from('<I',data,at)[0]
        cs=0xfffffffe if cs==0xffffffff else 1 if cs==0 else cs
        hives[n]=dict(sha256=sha(data),header_valid=data[:4]==b'regf',sequences_equal=a==b,checksum_valid=cs==struct.unpack_from('<I',data,508)[0])
    (run/(label+'-setupapi.log')).write_bytes(rr['F'].read('winnt/setupapi.log'))
    return hives
fixture=read(k.parent/'usb-identification207/fixture-emu001.json');startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
if mode=='stage':
    assert not run.exists();review=read(k.parent/'usb-no-xid-control/build-review.json');assert review['passed'];build=k.parent/'usb-no-xid-control/artifacts'/review['attempt']
    if phase==1:
        parent=repo/'outputs/usb-identification207/artifacts/emu001/seed.qcow2'
        relative='../../../outputs/usb-identification207/artifacts/emu001/seed.qcow2';parenthash=filehash(parent)
        assert parenthash=='7c09d05af676a7c37f242850837a8b2fa19b81a6ae63b2af2ec156e9a5fa197b';expected=fixture['files'].copy();files={}
    else:
        parent=repo/'work/runs/nt5noxid-emu001/hdd.qcow2';relative='../nt5noxid-emu001/hdd.qcow2'
        assert (parent.parent/'cleanup.json').exists() and read(k.parent/'usb-no-xid-control/emu001/qualification.json')['scoped_restart_passed']
        parenthash=filehash(parent);assert parenthash=='6de11f0ce947138eddbabfa503836f3bb4b7eb51905795238a489f1236584f97';files=read(parent.parent/'stage.json')['files'].copy();expected={**fixture['protected'],**files}
    run.mkdir();subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',relative,str(disk)],check=True)
    with ColdIO(disk) as io:
        rr=readers(io)
        for n,h in expected.items():v,p=n.split('/',1);assert sha(rr[v].read(p))==h,n
        for row in review['providers'].values():v,p=row['fixture_path'].split('/',1);assert sha(rr[v].read(p))==row['sha256']
        assert missing(rr['F'],'winnt/system32/drivers/xwnxid.sys')
        capture(rr,'before')
        storage={n:dict(expected=h,actual=sha(rr[n.split('/',1)[0]].read(n.split('/',1)[1]))) for n,h in fixture['protected'].items() if n.endswith(('xwnfatx.sys','atapi.sys','ntoskrnl.exe','halxboxnt5.dll','freeldr.sys'))}
        assert all(v['actual']==v['expected'] for v in storage.values())
        (k/'storage-pins.json').write_text(json.dumps(dict(parent_path=str(parent),parent_sha256=parenthash,files=storage,physical_access=False),indent=2)+'\n')
        if phase==2:
            for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt','setupapi.log']:
                assert (run/('before-'+name)).read_bytes()==(parent.parent/('after-'+name)).read_bytes(),name
    class OnlyF(m.SliceIO):
        def write(self,data):
            start,size=m.fatx.PARTITIONS['F'];assert start<=self.pos and self.pos+len(data)<=start+size
            return super().write(data)
    io=OnlyF(disk);rr=readers(io)
    pairs=[('control.exe','control.exe'),('wizard.exe','wizard.exe')] if phase==1 else [('control.exe','verify.exe')]
    for source,target in pairs:
        data=(build/source).read_bytes();assert sha(data)==review['files'][source]
        path='xwnctl/'+target;rr['F'].write(path,data);files['F/'+path]=sha(data)
    executable='control.exe /first' if phase==1 else 'verify.exe /second'
    command=('@echo off\r\nC:\\xwnctl\\'+executable+'\r\necho %errorlevel% > C:\\xwnctl\\exit'+str(phase)+'.txt\r\nexit\r\n').encode('ascii')
    restore(rr['F'],startup,command);files['F/'+startup]=sha(command);rr['F'].flush()
    with ColdIO(disk) as io:
        rr=readers(io)
        for n,h in {**expected,**files}.items():v,p=n.split('/',1);assert sha(rr[v].read(p))==h,n
        assert missing(rr['F'],'winnt/system32/drivers/xwnxid.sys')
    scan(disk,k/case/'before/artifacts');a=read(k/case/'before/allocation.json')
    assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
    assert filehash(parent)==parenthash
    r=dict(case=case,phase=phase,physical_access=False,files=files,baseline_exact=True,allocation_passed=True,
        staged_disk_sha256=filehash(disk),parent_path=str(parent),parent_sha256=parenthash,xid_driver_absent=True)
    (run/'stage.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS no-XID fixture phase',phase)
else:
    assert (run/'cleanup.json').exists() and not (k/(case+'-review.json')).exists()
    stage=read(run/'stage.json');checks={};logs={};errors=[]
    with ColdIO(disk) as io:
        rr=readers(io)
        for n,h in {**fixture['protected'],**stage['files']}.items():v,p=n.split('/',1);checks[n]=sha(rr[v].read(p))==h
        checks['xid_driver_absent']=missing(rr['F'],'winnt/system32/drivers/xwnxid.sys')
        for n in ['status'+str(phase)+'.log','payload'+str(phase)+'.txt','exit'+str(phase)+'.txt']+(['wizard201.log'] if phase==1 else []):
            try:data=rr['F'].read('xwnctl/'+n)
            except Exception as e:errors.append(dict(file=n,error=str(e)));continue
            (run/n).write_bytes(data);logs[n]=dict(length=len(data),sha256=sha(data),ascii_text=all(v in [9,10,13] or 32<=v<127 for v in data))
        hives=capture(rr,'after')
    scan(disk,k/case/'after/artifacts');a=read(k/case/'after/allocation.json');obs=read(run/'observe.json')
    expected=bytes(33+(i*17+phase*11)%90 for i in range(2226));p=run/('payload'+str(phase)+'.txt')
    r=dict(case=case,phase=phase,physical_access=False,checks=checks,protected_exact=all(checks.values()),hives=hives,
        logs=logs,payload_exact=p.exists() and p.read_bytes()==expected,expected_payload_sha256=sha(expected),
        allocation_consistent=a['allocation_consistent'],allocation_errors=a['errors'],orphan_cluster_count=a['orphan_cluster_count'],
        collection_errors=errors,dashboard_returned=obs.get('dashboard_returned',False))
    (k/(case+'-review.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
