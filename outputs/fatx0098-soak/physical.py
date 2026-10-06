"""One timed FATX0098 storage soak; no driver, video or trace reseeding."""
import argparse,datetime,ftplib,hashlib,importlib.util,io,json,os,socket
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];art=k/'artifacts/physical';record=k/'physical.json'
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
directory='/F/xwns98';driver='/F/winnt/system32/drivers/xwnfatx.sys'
test_startup=b'@echo off\r\nC:\\xwns98\\probe.exe\r\nexit\r\n'
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
baseline=json.loads((ws/'outputs/release-0.1.0/release.json').read_text())
expected=dict(baseline['physical_drivers_and_loader'])
expected['/F/winnt/system32/drivers/xboxvnt5.sys']='3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'
expected['/F/winnt/system32/framebuf.dll']='5da1fe7c3cdaf67a4a487c8872c2034fbc425bfd36d2b7715b2a1c4caa51df86'
candidate_sha='beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd'
expected[driver]=candidate_sha
class FTP(ftplib.FTP):
    def ntransfercmd(self,*args,**kwargs):
        sock,n=super().ntransfercmd(*args,**kwargs);sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return sock,n
def connect():
    f=FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=20);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD']);return f
    except BaseException:f.close();raise
def get(f,path,optional=False):
    b=io.BytesIO()
    def receive(data):
        assert b.tell()+len(data)<=200*1024*1024;b.write(data)
    try:f.retrbinary('RETR '+path,receive,65536)
    except ftplib.error_perm as exc:
        if optional and str(exc).startswith('550'):return None
        raise
    return b.getvalue()
def put(f,path,data):
    for at in range(0,max(1,len(data)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
    assert get(f,path)==data,path
def preserve(name,data):
    art.mkdir(parents=True,exist_ok=True);p=art/name
    if p.exists():assert p.read_bytes()==data,'Evidence changed: '+name
    else:p.write_bytes(data)
    return dict(bytes=len(data),sha256=sha(data))
def save(r,path=record):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(path)
def owner(f):
    assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==json.loads((ws/'outputs/native-windows-physical-f/physical-cache-preflight.json').read_text())['ownership_marker']
def missing(f,path):
    parent,name=path.rsplit('/',1);f.cwd(parent);lines=[];f.retrlines('LIST',lines.append)
    entries=[v.split(None,8) for v in lines];assert all(len(v)==9 for v in entries)
    assert all(v[8].lower()!=name.lower() for v in entries),'Preserve existing directory '+path
def checks(f,candidate=False):
    values=dict(expected)
    if candidate:values[driver]=candidate_sha
    return {p:dict(sha256=sha(get(f,p)),expected=h) for p,h in values.items()}
def passed(rows):return all(v['sha256']==v['expected'] for v in rows.values())
def main(action):
    with connect() as f:
        owner(f)
        if action=='check':
            r=dict(scope='Read-only baseline preflight; no deployment or launch',utc=utc(),checks=checks(f),startup_sha256=sha(get(f,startup)))
            r['passed']=passed(r['checks']) and r['startup_sha256']==baseline['startup_sha256'];save(r,k/'preflight.json');print(json.dumps(r,indent=2));return
        if action=='deploy-launch':
            assert not record.exists(),'Never repeat this deployment/launch'
            eligibility=json.loads((k/'eligibility.json').read_text())
            assert eligibility['eligible_for_controlled_trial'] and sha((k/'rehearsal/audit.json').read_bytes())==eligibility['audit_sha256']
            assert json.loads((k.parent/'fatx0098-physical-trial/qualification.json').read_text())['passed']
            review=json.loads((k/'probe-review.json').read_text());probe=(k/'artifacts/probe.exe').read_bytes()
            assert review['passed'] and sha(probe)==review['probe_sha256']
            fixture=json.loads((k/'fixture-rehearsal.json').read_text());assert next(v['sha256'] for v in fixture['payloads'] if v['path']=='xwns98/probe.exe')==sha(probe)
            for name in ['probe','matched']:
                rev=json.loads((k/(name+'-review.json')).read_text());assert rev['passed'] and sha((k/'artifacts'/(name+'.exe')).read_bytes())==rev['probe_sha256']
                assert next(v['sha256'] for v in fixture['payloads'] if v['path']=='xwns98/'+name+'.exe')==rev['probe_sha256']
            assert next(v['sha256'] for v in fixture['payloads'] if v['path']=='xwns98/scribble.bmp')==sha((k/'artifacts/scribble.bmp').read_bytes())
            assert passed(checks(f));original=get(f,startup);assert sha(original)==baseline['startup_sha256'];missing(f,directory)
            candidate=(k.parent/'fatx-paging-eof/artifacts/xwnfatx.sys').read_bytes();assert sha(candidate)==candidate_sha
            old=get(f,driver);assert sha(old)==expected[driver]
            r=dict(scope=__doc__,created_utc=utc(),launch_attempted=False,startup_enabled=False,candidate_sha256=candidate_sha,probe_sha256=sha(probe),preserved={},payloads=[],video_unchanged_sha256=expected['/F/winnt/system32/drivers/xboxvnt5.sys'],eligibility=eligibility)
            for name,data in [('before-startup.cmd',original),('before-xwnfatx.sys',old),('before-trace.bin',get(f,'/F/winnt/system32/xwn-video-trace.bin')),('before-system.evt',get(f,'/F/winnt/system32/config/sysevent.evt')),('before-application.evt',get(f,'/F/winnt/system32/config/appevent.evt'))]:r['preserved'][name]=preserve(name,data)
            save(r)
            try:
                f.mkd(directory)
                for path,data in [(directory+'/rollback.sys',old),(directory+'/startup.cmd',original)]+[(directory+'/'+n,(k/'artifacts'/n).read_bytes()) for n in ['probe.exe','matched.exe','scribble.bmp']]:
                    put(f,path,data);r['payloads'].append(dict(path=path,bytes=len(data),sha256=sha(data)));save(r)
                assert old==candidate;r['driver_unchanged_utc']=utc();save(r)
                assert passed(checks(f,True));put(f,startup,test_startup);r['startup_enabled']=True;save(r)
            except Exception as exc:
                r['prelaunch_error']=repr(exc);save(r)
                put(f,startup,original)
                r.update(startup_enabled=False,prelaunch_rollback=True);save(r);raise
            r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save(r)
            try:r['reply']=f.sendcmd(r['command'])
            except ftplib.all_errors as exc:r['reply_uncertain']=type(exc).__name__
            save(r);print('One physical trial launch recorded:',r.get('reply',r.get('reply_uncertain')),flush=True)
        else:
            r=json.loads(record.read_text());original=(art/'before-startup.cmd').read_bytes();assert sha(original)==baseline['startup_sha256']
            assert get(f,startup) in [test_startup,original]
            put(f,startup,original);r['startup_enabled']=False;save(r)
            if action=='collect':
                assert r['launch_attempted'] and not r.get('collected_utc')
                r['collected']={}
                files={'result.log':directory+'/result.log','system.evt':'/F/winnt/system32/config/sysevent.evt','application.evt':'/F/winnt/system32/config/appevent.evt','trace.bin':'/F/winnt/system32/xwn-video-trace.bin'}
                from workload import NAMES,ABSENT
                manual=['manual-paint.bmp','manual-paint2.bmp','manual-note.txt']
                files.update({name:directory+'/'+name for name in NAMES+ABSENT+manual})
                for name,path in files.items():
                    data=get(f,path,optional=name in NAMES+ABSENT+manual)
                    r['collected'][name]=preserve('after-'+name,data) if data is not None else None;save(r)
                r['candidate_checks']=checks(f,True)
                r['probe_unchanged']=sha(get(f,directory+'/probe.exe'))==r['probe_sha256']
                r['rollback_exact']=sha(get(f,directory+'/rollback.sys'))==expected[driver]
                r['helper_checks']={n:sha(get(f,directory+'/'+n))==sha((k/'artifacts'/n).read_bytes()) for n in ['probe.exe','matched.exe','scribble.bmp']}
                r['collected_utc']=utc();save(r);print('Physical evidence collected; startup disabled; qualification pending')
            elif action=='restore-startup':
                r['startup_restored_utc']=utc();save(r);print('Original startup restored; no driver write or Windows launch')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['check','deploy-launch','collect','restore-startup']);main(parser.parse_args().action)
