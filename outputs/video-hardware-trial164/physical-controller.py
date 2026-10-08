"""Single nonpromoting physical drawing diagnostic; preserve and restore0093 baseline."""
import argparse,datetime,hashlib,importlib.util,json,zipfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];record=k/'physical.json';art=k/'artifacts/physical'
spec=importlib.util.spec_from_file_location('ftp_helpers',k.parent/'fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
startup=m.startup;test_startup=b'@echo off\r\nC:\\xwnv164\\runner.exe\r\nexit\r\n'
capture=read(k.parent/'video-physical-review159/capture.json')
sources=read(k.parent/'video-hardware-candidate158/package-review.json')['candidate']
changes=[('/'+v['target'],ws/v['source'],v['sha256']) for v in sources]
system='/F/winnt/system32/config/system';xwnown='/F/winnt/system32/xwnown.dll'
proposal=k.parent/'video-physical-review159/artifacts/proposed-system'
proposal_sha=read(k.parent/'video-physical-review159/binding-edit.json')['after_sha256']

def save(r):
    tmp=record.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');tmp.replace(record)
def preserve(name,data):
    p=art/name;assert not p.exists();p.write_bytes(data)
    return dict(path=str(p.relative_to(ws)).replace('\\','/'),bytes=len(data),sha256=sha(data))
def absence(f,directory,name):
    f.cwd(directory);lines=[];f.retrlines('LIST',lines.append)
    entries=[v.split(None,8) for v in lines];assert all(len(v)==9 for v in entries)
    return all(v[8].lower()!=name.lower() for v in entries)
def restore(f,r):
    # Startup always restored first. Keep after evidence before calling this after a run.
    m.put(f,startup,(art/'before-startup.cmd').read_bytes());r['startup_enabled']=False;save(r)
    for path,_,_ in changes:
        before=r['before_payloads'][path]
        if before is None:
            current=m.get(f,path,optional=True)
            expected=next(v[2] for v in changes if v[0]==path)
            if current is not None:
                assert sha(current)==expected,'Unknown file would be deleted during rollback'
                f.delete(path)
                assert absence(f,path.rsplit('/',1)[0],path.rsplit('/',1)[1])
        else:m.put(f,path,(ws/before['path']).read_bytes())
    m.put(f,system,(art/'before-system').read_bytes())
    r['baseline_restored']=True;r['restored_utc']=m.utc();save(r)
def ready():
    r=read(k.parent/'video-helper-runtime165/candidate001/audit.json');assert r['workload_passed'] and r['integrity_passed']
    assert len(r['warnings_errors'])==1 and r['warnings_errors'][0]['source']=='Ftdisk' and r['warnings_errors'][0]['event_id']==49
    assert not r['strict_qualification_passed']
    control=read(k.parent/'video-physical-rehearsal162/control001/audit.json')
    fields=['source','event_id','type','strings','data_hex']
    assert len(control['warnings_errors'])==1 and all(r['warnings_errors'][0][f]==control['warnings_errors'][0][f] for f in fields)
    assert r['copy_checks_passed'] and r['loop_coverage'] and r['normal_shutdown_count']==1
    assert read(k.parent/'video-physical-diagnostic163/diagnostic-review.json')['display_compatibility_passed']
    assert read(k/'build-review.json')['passed'] and sha((k/'artifacts/runner.exe').read_bytes())==read(k/'build-review.json')['sha256']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['deploy-launch','collect','rollback']);parser.add_argument('--keyboard-unplugged',action='store_true');a=parser.parse_args()
    if a.action=='deploy-launch':
        assert a.keyboard_unplugged,'Require actual user-reported unplugged Razer/dashboard state'
        ready();assert not record.exists();art.mkdir(exist_ok=False)
        r=dict(scope=__doc__,physical_result=True,physical_qualified=False,strict_qualification_passed=False,
               expected_baseline_error='Ftdisk49 remains a strict failure; this is a nonpromoting drawing diagnostic',
               before_payloads={},launch_requested=False,startup_enabled=False,baseline_restored=False,
               emulator_audit_sha256=sha((k.parent/'video-helper-runtime165/candidate001/audit.json').read_bytes()),keyboard_user_reported_unplugged=True)
        with m.connect() as f:
            m.owner(f)
            for row in capture['files']:
                # Config/log/trace freshness is checked too, before any write.
                assert sha(m.get(f,row['path']))==row['sha256'],'Physical baseline drift: '+row['path']
            assert absence(f,'/F','xwnv164') and absence(f,'/F','xwn-display164')
            for path,p,digest in changes:
                assert sha(p.read_bytes())==digest
                if path==xwnown and absence(f,'/F/winnt/system32','xwnown.dll'):data=None
                else:data=m.get(f,path)
                r['before_payloads'][path]=None if data is None else preserve('before-'+p.name,data)
            for name,path in [('startup.cmd',startup),('system',system),('software','/F/winnt/system32/config/software'),
                ('sysevent.evt','/F/winnt/system32/config/sysevent.evt'),('appevent.evt','/F/winnt/system32/config/appevent.evt'),
                ('trace.bin','/F/winnt/system32/xwn-video-trace.bin')]:preserve('before-'+name,m.get(f,path))
            assert sha(proposal.read_bytes())==proposal_sha;save(r)
            # Readback-verified local and console rollback copies precede payload changes.
            rollback=art/'current-rollback164.zip'
            with zipfile.ZipFile(rollback,'x',compression=zipfile.ZIP_DEFLATED) as z:
                for p in art.glob('before-*'):z.writestr(p.name,p.read_bytes())
            with zipfile.ZipFile(rollback) as z:assert all(z.read(p.name)==p.read_bytes() for p in art.glob('before-*'))
            r['rollback_sha256']=sha(rollback.read_bytes());save(r)
            f.mkd('/F/xwn-display164');m.put(f,'/F/xwn-display164/current-rollback164.zip',rollback.read_bytes())
            f.mkd('/F/xwnv164')
            m.put(f,'/F/xwnv164/runner.exe',(k/'artifacts/runner.exe').read_bytes())
            m.put(f,'/F/xwnv164/replay.exe',(k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe').read_bytes())
            try:
                for path,p,_ in changes:m.put(f,path,p.read_bytes())
                m.put(f,system,proposal.read_bytes())
                m.put(f,startup,test_startup);r['startup_enabled']=True;save(r)
            except Exception as exc:
                r['prelaunch_failure']=repr(exc);save(r);restore(f,r);raise
            r['launch_requested']=True;r['launch_utc']=m.utc();r['command']=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe';save(r)
            try:r['reply']=f.sendcmd(r['command'])
            except Exception as exc:r['reply_uncertain']=type(exc).__name__
            save(r);print('Single hardware drawing diagnostic requested; never repeat')
    else:
        r=read(record)
        with m.connect() as f:
            m.owner(f)
            if a.action=='collect':
                assert r['launch_requested'] and not r.get('collected_utc')
                m.put(f,startup,(art/'before-startup.cmd').read_bytes());r['startup_enabled']=False;save(r)
                r['after']={}
                for name,path in [('attempt.log','/F/xwnv164/attempt.log'),('gdi-baseline.txt','/F/xwnv164/gdi-baseline.txt'),
                    ('sysevent.evt','/F/winnt/system32/config/sysevent.evt'),('appevent.evt','/F/winnt/system32/config/appevent.evt'),
                    ('system',system),('software','/F/winnt/system32/config/software'),('setupapi.log','/F/winnt/setupapi.log'),
                    ('trace.bin','/F/winnt/system32/xwn-video-trace.bin')]+[(p.rsplit('/',1)[1],p) for p,_,_ in changes]:
                    data=m.get(f,path,optional=name in ['attempt.log','gdi-baseline.txt'])
                    r['after'][name]=None if data is None else preserve('after-'+name,data);save(r)
                r['collected_utc']=m.utc();save(r);restore(f,r)
                print('Startup restored first; result preserved; original display/SYSTEM restored')
            else:
                assert not r.get('baseline_restored');restore(f,r);print('Original baseline restored; no launch')
