"""One physical baseline GDI measurement; no driver or display-mode changes."""
import argparse,datetime,ftplib,hashlib,io,json,os
from pathlib import Path

k=Path(__file__).resolve().parent;ws=k.parents[2]
record=k/'trial.json';art=k/'artifacts/physical'
release=json.loads((ws/'outputs/release-0.1.0/release.json').read_text())
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
remote='/F/xwngdi01'
script=b'@echo off\r\nC:\\xwngdi01\\runner.exe\r\nexit\r\n'
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

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['launch','collect'])
    a=parser.parse_args()
    art.mkdir(parents=True,exist_ok=True)
    with ftplib.FTP() as f:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=20)
        f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        marker=json.loads(get(f,'/F/xwn-deploy-v1.json'))
        assert marker==json.loads((ws/'outputs/native-windows-physical-f/physical-cache-preflight.json').read_text())['ownership_marker']
        if a.action=='launch':
            assert not record.exists(), 'Never repeat an existing launch record'
            assert json.loads((k.parent/'probe-v3/emulator-audit.json').read_text())['passed']
            build=json.loads((k/'build-review.json').read_text());assert build['passed']
            checks=verify(f);assert all(checks.values()), 'Physical baseline changed'
            baseline=get(f,startup);assert sha(baseline)==release['startup_sha256']
            try:f.cwd(remote)
            except ftplib.error_perm as exc:
                if not (str(exc).startswith('550') or str(exc).startswith('553') and 'Directory not found' in str(exc)):raise
                f.cwd('/F');lines=[];f.retrlines('LIST',lines.append)
                entries=[line.split(None,8) for line in lines]
                assert all(len(parts)==9 for parts in entries)
                assert all(parts[8].lower()!='xwngdi01' for parts in entries)
            else:raise RuntimeError('Test directory already exists; preserve it')
            payloads={'runner.exe':(k/'artifacts/runner.exe').read_bytes(),
                      'replay.exe':(k.parent/'probe-v3/artifacts/gdi-probe.exe').read_bytes()}
            for row in build['files']:assert sha(payloads[row['name']])==row['sha256']
            r=dict(scope=__doc__,started_utc=utc(),launch_attempted=False,startup_enabled=False,
                   baseline_checks=checks,payloads=build['files'],preserved={},physical_result=True)
            r['preserved']['startup.cmd']=preserve('before-startup.cmd',baseline)
            for label,path in [('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt')]:
                r['preserved'][label]=preserve('before-'+label,get(f,path))
            save()
            try:
                f.mkd(remote)
                for name,data in payloads.items():put(f,remote+'/'+name,data)
                r['startup_install_requested']=True;save()
                put(f,startup,script);r['startup_enabled']=True;save()
                assert all(verify(f).values())
                r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save()
                try:r['reply']=f.sendcmd(r['command'])
                except ftplib.all_errors as exc:r['reply_uncertain']=type(exc).__name__
                save();print(json.dumps(dict(launch_attempted=True,reply=r.get('reply'),uncertain=r.get('reply_uncertain'))))
            except Exception as exc:
                r['error']=repr(exc);save()
                if not r['launch_attempted']:
                    put(f,startup,baseline);r['startup_enabled']=False;save()
                raise
        else:
            r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc')
            baseline=(art/'before-startup.cmd').read_bytes();assert sha(baseline)==release['startup_sha256']
            current=get(f,startup);assert current in (baseline,script)
            if current!=baseline:put(f,startup,baseline)
            r['startup_enabled']=False;save()
            r['collected']={}
            for name,path in [('gdi-baseline.txt',remote+'/gdi-baseline.txt'),('attempt.log',remote+'/attempt.log'),
                              ('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt')]:
                data=get(f,path,optional=name.endswith(('.txt','.log')))
                r['collected'][name]=preserve('after-'+name,data) if data is not None else None;save()
            r['baseline_checks_after']=verify(f)
            r['payload_checks_after']={row['name']:sha(get(f,remote+'/'+row['name']))==row['sha256'] for row in r['payloads']}
            r['collected_utc']=utc();r['qualification']='Pending probe/event review; dashboard return alone is not PASS';save()
            print('Collected physical logs; original startup restored and verified')
