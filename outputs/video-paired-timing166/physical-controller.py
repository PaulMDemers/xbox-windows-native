"""Single nonpromoting physical drawing diagnostic; preserve and restore0093 baseline."""
import argparse,datetime,hashlib,importlib.util,json,zipfile,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[2];assert case in ['control001','candidate001']
namespace='xwnvt166a' if case=='control001' else 'xwnvt166b'
rollback_dir='xwn-display166a' if case=='control001' else 'xwn-display166b'
record=k/case/'physical.json';art=k/case/'artifacts/physical'
spec=importlib.util.spec_from_file_location('ftp_helpers',k.parent/'fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
startup=m.startup;test_startup=('@echo off\r\nC:\\'+namespace+'\\runner.exe\r\nexit\r\n').encode('ascii')
capture=read(k.parent/'video-physical-review159/capture.json')
sources=read(k.parent/'video-hardware-candidate158/package-review.json')['candidate']
all_changes=[('/'+v['target'],ws/v['source'],v['sha256']) for v in sources]
changes=all_changes if case=='candidate001' else []
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
    packet=read(k/'physical-ready.json')
    for name,digest in packet['source_pins'].items():assert sha((k/name).read_bytes())==digest,name
    fields=['source','event_id','type','strings','data_hex']
    expected=read(k.parent/'video-physical-rehearsal162/control001/audit.json')['warnings_errors']
    for name in ['control001','candidate001']:
        r=read(k/name/'audit.json')
        assert r['workload_passed'] and r['integrity_passed'] and not r['strict_qualification_passed']
        assert len(r['warnings_errors'])==len(expected)==1 and all(r['warnings_errors'][0][f]==expected[0][f] for f in fields)
        assert not r['new_events']['application'] and r['normal_shutdown_count']==1
    review=read(k/'build-review.json')
    assert review['passed'] and sha((k/'artifacts/runner.exe').read_bytes())==review['sha256']
    assert sha((k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe').read_bytes())==review['probe_sha256']
    if case=='candidate001':
        r=read(k/'control001/physical-audit.json')
        assert r['workload_passed'] and r['preserved_files_exact'] and r['event_history_preserved']
        assert not r['new_events']['application'] and len(r['warnings_errors'])==1
        assert all(r['warnings_errors'][0][f]==expected[0][f] for f in fields)
        assert read(k/'control001/restored-verification.json')['passed']
        assert read(k/'control001/physical-hive-audit.json')['passed']
        assert r['actual_caps']==read(k/'control001/audit.json')['actual_caps']
        assert not any(v['source']=='Application Popup' for v in r['new_events']['system'])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['deploy-launch','collect','rollback']);parser.add_argument('case',choices=['control001','candidate001']);parser.add_argument('--keyboard-unplugged',action='store_true');a=parser.parse_args()
    if a.action=='deploy-launch':
        assert a.keyboard_unplugged,'Require actual user-reported unplugged Razer/dashboard state'
        ready();assert not record.exists();art.mkdir(exist_ok=False)
        r=dict(scope=__doc__,physical_result=True,physical_qualified=False,strict_qualification_passed=False,
               expected_baseline_error='Ftdisk49 remains a strict failure; this is a nonpromoting drawing diagnostic',
               before_payloads={},launch_requested=False,startup_enabled=False,baseline_restored=False,
               case=case,namespace=namespace,emulator_audit_sha256=sha((k/case/'audit.json').read_bytes()),keyboard_user_reported_unplugged=True)
        with m.connect() as f:
            m.owner(f)
            for row in capture['files']:
                if row['path'].endswith(('/config/software','/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')):continue
                # All immutable core, startup and restored SYSTEM must match.
                assert sha(m.get(f,row['path']))==row['sha256'],'Physical baseline drift: '+row['path']
            assert absence(f,'/F',namespace) and absence(f,'/F',rollback_dir)
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
            rollback=art/'current-rollback166.zip'
            with zipfile.ZipFile(rollback,'x',compression=zipfile.ZIP_DEFLATED) as z:
                for p in art.glob('before-*'):z.writestr(p.name,p.read_bytes())
            with zipfile.ZipFile(rollback) as z:assert all(z.read(p.name)==p.read_bytes() for p in art.glob('before-*'))
            r['rollback_sha256']=sha(rollback.read_bytes());save(r)
            f.mkd('/F/'+rollback_dir);m.put(f,'/F/'+rollback_dir+'/current-rollback166.zip',rollback.read_bytes())
            f.mkd('/F/'+namespace)
            m.put(f,'/F/'+namespace+'/runner.exe',(k/'artifacts/runner.exe').read_bytes())
            m.put(f,'/F/'+namespace+'/replay.exe',(k.parent/'video-next/probe-v3/artifacts/gdi-probe.exe').read_bytes())
            try:
                for path,p,_ in changes:m.put(f,path,p.read_bytes())
                if case=='candidate001':m.put(f,system,proposal.read_bytes())
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
                for name,path in [('attempt.log','/F/'+namespace+'/attempt.log'),
                    *[('sample%d'%i,'/F/'+namespace+'/sample%d/gdi-baseline.txt'%i) for i in range(5)],
                    ('sysevent.evt','/F/winnt/system32/config/sysevent.evt'),('appevent.evt','/F/winnt/system32/config/appevent.evt'),
                    ('system',system),('software','/F/winnt/system32/config/software'),('setupapi.log','/F/winnt/setupapi.log'),
                    ('trace.bin','/F/winnt/system32/xwn-video-trace.bin')]+[(p.rsplit('/',1)[1],p) for p,_,_ in all_changes]:
                    data=m.get(f,path,optional=name=='attempt.log' or name.startswith('sample') or name=='xwnown.dll')
                    r['after'][name]=None if data is None else preserve('after-'+name,data);save(r)
                r['collected_utc']=m.utc();save(r);restore(f,r)
                print('Startup restored first; result preserved; original display/SYSTEM restored')
            else:
                assert not r.get('baseline_restored');restore(f,r);print('Original baseline restored; no launch')
