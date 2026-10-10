"""Owned offline staging and cold extraction. Never opens physical console FTP."""
import hashlib,importlib,json,re,struct,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1];mode,case=sys.argv[1:]
assert re.fullmatch('emu[0-9]{3}',case)
run=repo/('work/runs/nt5xid-'+case);disk=run/'hdd.qcow2'
canon=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'outputs/native-windows-paint-save'),str(canon/'outputs/fatx-mapped-eof'),str(canon/'outputs/device-observation188')]
from coldio import ColdIO
from allocation import scan
from restore import restore
m=importlib.import_module('prepare-fixture');m.target=disk;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
fixture=read(k.parent/'usb-identification207/fixture-emu001.json')
def readers(io):return {v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
if mode=='stage':
    assert not (run/'stage.json').exists()
    review=read(k/'build-review.json');assert review['passed']
    build=k/'artifacts'/review['attempt'];files={}
    with ColdIO(disk) as io:
        rr=readers(io)
        for name,digest in fixture['files'].items():
            v,p=name.split('/',1);assert sha(rr[v].read(p))==digest,name
        for name,row in review['providers'].items():
            volume,relative=row['fixture_path'].split('/',1)
            assert sha(rr[volume].read(relative))==row['sha256'],name
        for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
            (run/('before-'+name)).write_bytes(rr['F'].read('winnt/system32/config/'+name))
        (run/'before-setupapi.log').write_bytes(rr['F'].read('winnt/setupapi.log'))
    class OnlyF(m.SliceIO):
        def write(self,data):
            start,size=m.fatx.PARTITIONS['F'];assert start<=self.pos and self.pos+len(data)<=start+size
            return super().write(data)
    io=OnlyF(disk);rr=readers(io)
    for name in ['xwnxid.sys','xwnxid.inf','probe.exe']:
        data=(build/name).read_bytes();assert sha(data)==review['files' if name.endswith(('.sys','.exe')) else 'inputs'][name]
        rr['F'].write('xwnxid/'+name,data);files['F/xwnxid/'+name]=sha(data)
    command=b'@echo off\r\nC:\\xwnxid\\probe.exe\r\necho %errorlevel% > C:\\xwnxid\\exit.txt\r\nexit\r\n'
    restore(rr['F'],startup,command);files['F/'+startup]=sha(command)
    rr['F'].flush()
    with ColdIO(disk) as io:
        rr=readers(io)
        for name,digest in {**fixture['files'],**files}.items():
            v,p=name.split('/',1);assert sha(rr[v].read(p))==digest,name
    scan(disk,k/case/'before/artifacts');a=read(k/case/'before/allocation.json')
    assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
    r=dict(physical_access=False,case=case,build=review['attempt'],build_files=review['files'],files=files,baseline_exact=True,allocation_passed=True)
    (run/'stage.json').write_text(json.dumps(r,indent=2)+'\n');print('Staged emulator package, providers, baseline and allocation verified')
elif mode=='audit':
    assert (run/'cleanup.json').exists() and not (k/(case+'-review.json')).exists()
    errors=[];checks={};hives={};log=b'';stage=read(run/'stage.json')
    with ColdIO(disk) as io:
        rr=readers(io)
        for name in ['probe.log','exit.txt']:
            try:data=rr['F'].read('xwnxid/'+name);(run/name).write_bytes(data)
            except Exception as e:errors.append(name+': '+str(e));continue
            if name=='probe.log':log=data
        for name,digest in fixture['protected'].items():
            v,p=name.split('/',1);checks[name]=sha(rr[v].read(p))==digest
        for name,digest in stage['files'].items():
            v,p=name.split('/',1);checks[name]=sha(rr[v].read(p))==digest
        try:checks['installed_driver_exact']=sha(rr['F'].read('winnt/system32/drivers/xwnxid.sys'))==stage['build_files']['xwnxid.sys']
        except Exception as e:errors.append('installed driver: '+str(e))
        for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
            data=rr['F'].read('winnt/system32/config/'+name);(run/('after-'+name)).write_bytes(data)
            if name.endswith('.evt'):continue
            seq1,seq2=struct.unpack_from('<II',data,4);checksum=0
            for at in range(0,508,4):checksum^=struct.unpack_from('<I',data,at)[0]
            checksum=0xfffffffe if checksum==0xffffffff else 1 if checksum==0 else checksum
            hives[name]=dict(sha256=sha(data),sequences_equal=seq1==seq2,header_valid=data[:4]==b'regf',checksum_valid=checksum==struct.unpack_from('<I',data,508)[0])
        (run/'after-setupapi.log').write_bytes(rr['F'].read('winnt/setupapi.log'))
    scan(disk,k/case/'after/artifacts');a=read(k/case/'after/allocation.json')
    observation=read(run/'observe.json');text=log.decode('ascii','replace')
    r=dict(case=case,physical_access=False,hid_read_pass='HID_READ_PASS 000000c8' in text,
        driver_installed='INSTALL_RESULT 00000001' in text,normal_restart_requested='NORMAL_RESTART_REQUEST' in text,
        dashboard_returned=observation.get('dashboard_returned',False),checks=checks,protected_exact=all(checks.values()),hives=hives,
        allocation_consistent=a['allocation_consistent'],allocation_errors=a['errors'],orphan_cluster_count=a['orphan_cluster_count'],
        collection_errors=errors,log_sha256=sha(log),build=stage['build'],probe_log=text,
        limits='Idle emulated controller only. No deliberate control input, physical qualification, unplug/power-transition coverage or ordinary-boot durability claim.')
    r['input_smoke_pass']=r['hid_read_pass'] and r['driver_installed'] and r['protected_exact'] and not errors
    (k/(case+'-review.json')).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({n:r[n] for n in ['input_smoke_pass','driver_installed','hid_read_pass','dashboard_returned','collection_errors']}))
else:raise ValueError(mode)
