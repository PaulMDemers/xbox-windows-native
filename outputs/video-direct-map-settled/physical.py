"""Physical direct reserved-RAM experiment; one bounded GDI boot, then restore qualified0093."""
import argparse,datetime,ftplib,hashlib,io,json,os
from pathlib import Path

k=Path(__file__).resolve().parent;ws=k.parents[1]
record=k/'physical.json';art=k/'artifacts/physical'
release=json.loads((ws/'outputs/release-0.1.0/release.json').read_text())
release['physical_drivers_and_loader']['/F/winnt/system32/drivers/xboxvnt5.sys']='3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
trace='/F/winnt/system32/xwn-video-trace.bin'
trace_seed=b'XWN-VID-TRACE01\n'+bytes(4080)
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()

def get(f,path,optional=False):
    b=io.BytesIO()
    def receive(data):
        assert b.tell()+len(data)<=16*1024*1024
        b.write(data)
    try:f.retrbinary('RETR '+path,receive,65536)
    except ftplib.error_perm as exc:
        if optional and str(exc).startswith('550'):return None
        raise
    return b.getvalue()

def put(f,path,data):
    for at in range(0,max(1,len(data)),32768):
        f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
    assert get(f,path)==data

def preserve(name,data):
    p=art/name
    if p.exists():assert p.read_bytes()==data, 'Preserved evidence changed'
    else:p.write_bytes(data)
    return dict(bytes=len(data),sha256=sha(data))

def save():
    tmp=record.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(record)

def verify(f):
    return {path:sha(get(f,path))==expected for path,expected in release['physical_drivers_and_loader'].items()}

video='/F/winnt/system32/drivers/xboxvnt5.sys'
backup='/F/winnt/system32/drivers/xboxvnt5.trace015'
test_startup=b'@echo off\r\nC:\\xwnlag01\\runner.exe\r\nexit\r\n'

def check_candidate(f):
    expected=dict(release['physical_drivers_and_loader']);expected[video]=r['candidate_sha256']
    checks={p:sha(get(f,p))==h for p,h in expected.items()}
    checks[backup]=sha(get(f,backup))==release['physical_drivers_and_loader'][video]
    return checks

def missing_directory(f,path):
    try:f.cwd(path)
    except ftplib.error_perm as exc:
        if not (str(exc).startswith('550') or str(exc).startswith('553') and 'Directory not found' in str(exc)):raise
        f.cwd('/F');lines=[];f.retrlines('LIST',lines.append)
        entries=[v.split(None,8) for v in lines];assert all(len(v)==9 for v in entries)
        assert all(v[8].lower()!=path.rsplit('/',1)[1].lower() for v in entries)
    else:raise RuntimeError('Existing helper directory must be preserved')

if __name__=='__main__':
    p=argparse.ArgumentParser(description='One candidate deployment, one physical boot, explicit collection and rollback.')
    p.add_argument('action',choices=['deploy-launch','collect','rollback']);p.add_argument('--cycle',type=int,choices=[1],default=1)
    a=p.parse_args();art.mkdir(parents=True,exist_ok=True)
    with ftplib.FTP() as f:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=20);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==json.loads((ws/'outputs/native-windows-physical-f/physical-cache-preflight.json').read_text())['ownership_marker']
        if a.action=='deploy-launch':
            assert not record.exists(), 'Never repeat deployment'
            # Match the successful single-boot emulator protocol.
            evidence_dir=k
            emulator_audit=evidence_dir/'audit.json'
            assert json.loads(emulator_audit.read_text())['passed']
            fixture=json.loads((evidence_dir/'fixture.json').read_text())
            tested_video=next(v['sha256'] for v in fixture['payloads'] if v['path']=='winnt/system32/drivers/xboxvnt5.sys')
            tested_runner=next(v['sha256'] for v in fixture['payloads'] if v['path']=='xwnlag01/runner.exe')
            tested_trace=next(v['sha256'] for v in fixture['payloads'] if v['path']=='winnt/system32/xwn-video-trace.bin')
            assert tested_runner==sha((k/'artifacts/runner.exe').read_bytes())
            assert tested_trace==sha(trace_seed)
            eligibility=dict(kind='strict direct-RAM audit',audit=str(emulator_audit),audit_sha256=sha(emulator_audit.read_bytes()),fixture_sha256=sha((evidence_dir/'fixture.json').read_bytes()),initial_trace_clean=True,host_reseed_between_boots=False)
            build=json.loads((k/'compiled-tests.json').read_text());assert build['passed'] and build['sha256']==tested_video
            assert all(verify(f).values())
            original=get(f,startup);assert sha(original)==release['startup_sha256']
            old=get(f,video);oldtrace=get(f,trace)
            assert len(oldtrace)==4096 and oldtrace[:16]==trace_seed[:16]
            assert get(f,backup,True) is None
            for directory in ['/F/xwnlag01','/F/xwnlag02']:missing_directory(f,directory)
            candidate=(k/'artifacts/xboxvnt5.sys').read_bytes();assert sha(candidate)==build['sha256']
            r=dict(scope=__doc__,physical_result=True,candidate_sha256=sha(candidate),cycles=[],startup_enabled=False,preserved={},payloads=[],eligibility=eligibility)
            for name,data in [('startup.cmd',original),('miniport.sys',old),('trace.bin',oldtrace)]:r['preserved'][name]=preserve('before-'+name,data)
            for name,path in [('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt')]:r['preserved'][name]=preserve('before-'+name,get(f,path))
            save()
            try:
                put(f,backup,old)
                for directory in ['/F/xwnlag01','/F/xwnlag02']:f.mkd(directory)
                runner=(k/'artifacts/runner.exe').read_bytes();probe=(ws/'outputs/video-next/probe-v3/artifacts/gdi-probe.exe').read_bytes()
                review=json.loads((k/'build-review.json').read_text());assert review['passed']
                assert sha(runner)==review['files'][0]['sha256'] and sha(probe)==review['files'][1]['sha256']
                for path,data in [('/F/xwnlag01/runner.exe',runner),('/F/xwnlag01/replay.exe',probe),('/F/xwnlag02/replay.exe',probe)]:
                    put(f,path,data);r['payloads'].append(dict(path=path,sha256=sha(data)));save()
                # Initialize the trace once for this diagnostic run.
                put(f,trace,trace_seed);r['trace_sha256']=sha(trace_seed);save()
                put(f,video,candidate);assert all(check_candidate(f).values())
                put(f,startup,test_startup);r['startup_enabled']=True;save()
            except Exception:
                put(f,startup,original);put(f,video,old);put(f,trace,oldtrace)
                r['startup_enabled']=False;r['prelaunch_rollback']=True;save();raise
        else:
            r=json.loads(record.read_text())
        if a.action=='deploy-launch':
            cycle=1
            assert len(r['cycles'])==cycle-1
            row=dict(cycle=cycle,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe')
            r['cycles'].append(row);save()
            try:row['reply']=f.sendcmd(row['command'])
            except ftplib.all_errors as exc:row['reply_uncertain']=type(exc).__name__
            save();print(json.dumps(row))
        elif a.action=='collect':
            assert len(r['cycles'])==a.cycle, 'Collect only the most recently launched cycle'
            row=r['cycles'][a.cycle-1];assert row['cycle']==a.cycle and not row.get('collected_utc')
            current=get(f,startup);original=(art/'before-startup.cmd').read_bytes()
            assert current in [test_startup,original]
            put(f,startup,original);r['startup_enabled']=False;save()
            row['collected']={}
            for name,path in [('attempt.log',f'/F/xwnlag0{a.cycle}/attempt.log'),('gdi-baseline.txt',f'/F/xwnlag0{a.cycle}/gdi-baseline.txt'),
              ('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt'),('trace.bin',trace)]:
                data=get(f,path,optional=name.endswith(('.txt','.log')))
                row['collected'][name]=preserve(f'cycle{a.cycle}-'+name,data) if data is not None else None;save()
            row['candidate_checks']=check_candidate(f)
            row['payload_checks']={v['path']:sha(get(f,v['path']))==v['sha256'] for v in r['payloads']}
            data=get(f,trace);row['trace_valid']=len(data)==4096 and data[:16]==trace_seed[:16] and 1<=int.from_bytes(data[16:20],'little')<=254 and int.from_bytes(data[32:36],'little')==1;row['collected_utc']=utc();save()
            print('Startup restored; cycle collected; qualification pending')
        elif a.action=='rollback':
            assert sha(get(f,video)) in [r['candidate_sha256'],release['physical_drivers_and_loader'][video]]
            assert sha(get(f,backup))==release['physical_drivers_and_loader'][video]
            put(f,startup,(art/'before-startup.cmd').read_bytes())
            preserve('rollback-trace.bin',get(f,trace))
            put(f,video,(art/'before-miniport.sys').read_bytes());put(f,trace,trace_seed)
            assert all(verify(f).values())
            r.update(startup_enabled=False,rolled_back_utc=utc());save();print('Baseline restored without launch')

