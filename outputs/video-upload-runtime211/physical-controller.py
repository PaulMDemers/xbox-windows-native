"""Exact210 upload accounting OFF/ON, text bounds ON and scalar/body clocks OFF; restore0093 baseline after each, never promote."""
import argparse,hashlib,importlib.util,json,sys,zipfile
from pathlib import Path
from interval_policy import candidate_permitted
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[2];assert case in ['control001','candidate001']
namespace='xwnua211a' if case=='control001' else 'xwnua211b'
rollback_dir='xwn-display211a' if case=='control001' else 'xwn-display211b'
record=k/case/'physical.json';art=k/case/'artifacts/physical'
spec=importlib.util.spec_from_file_location('ftp_helpers',k.parent/'fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
capture=read(k/'capture.json');package=read(k/'package-review.json')
probe_providers=read(k/'probe-providers.json');assert probe_providers['passed']
capture['files'] += probe_providers['files']
changes=[('/'+v['target'],ws/v['source'],v['sha256']) for v in package['cases'][case]]
startup=m.startup;system='/F/winnt/system32/config/system';xwnown='/F/winnt/system32/xwnown.dll'
test_startup=('@echo off\r\nC:\\'+namespace+'\\runner.exe /physical\r\nexit\r\n').encode('ascii')
proposal=k/'artifacts/proposed-system';proposal_sha=package['proposal_sha256']
mutable_suffixes=('/config/system','/config/software','/config/default','/config/sam','/config/security',
    '/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')
aux=[('startup.cmd',startup),('system',system),
     *[(n,'/F/winnt/system32/config/'+n) for n in ['software','default','sam','security','sysevent.evt','appevent.evt']],
     ('setupapi.log','/F/winnt/setupapi.log'),('trace.bin','/F/winnt/system32/xwn-video-trace.bin')]

def save(r):
    tmp=record.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');tmp.replace(record)

def preserve(name,data):
    p=art/name
    if p.exists():assert p.read_bytes()==data,'Changed preserved evidence: '+name
    else:p.write_bytes(data)
    return dict(path=p.relative_to(ws).as_posix(),bytes=len(data),sha256=sha(data))

def absence(f,directory,name):
    f.cwd(directory);lines=[];f.retrlines('LIST',lines.append)
    entries=[v.split(None,8) for v in lines];assert all(len(v)==9 for v in entries)
    return all(v[8].lower()!=name.lower() for v in entries)

def fixed_checks(f):
    rows=[]
    for row in capture['files']:
        path=row['path']
        if path.endswith(mutable_suffixes):continue
        actual=sha(m.get(f,path));assert actual==row['sha256'],'Physical baseline drift: '+path
        rows.append(dict(path=path,sha256=actual))
    # SYSTEM must return exactly to this session's captured pre-trial bytes.
    assert sha(m.get(f,system))==next(v['sha256'] for v in capture['files'] if v['path']==system)
    return rows

def restore(f,r):
    m.put(f,startup,(art/'before-startup.cmd').read_bytes());r['startup_enabled']=False;save(r)
    for path,_,expected in changes:
        before=r['before_payloads'][path]
        if before is None:
            current=m.get(f,path,optional=True)
            if current is not None:
                assert sha(current)==expected,'Unknown file would be deleted during rollback'
                f.delete(path)
            assert absence(f,path.rsplit('/',1)[0],path.rsplit('/',1)[1])
        else:
            data=(ws/before['path']).read_bytes();assert sha(data)==before['sha256'];m.put(f,path,data)
    m.put(f,system,(art/'before-system').read_bytes())
    r['restored_fixed_checks']=fixed_checks(f)
    r.update(baseline_restored=True,restored_utc=m.utc());save(r)

def ready():
    p=read(k/'physical-ready.json');assert p['prepared'] and package['passed'] and capture['passed']
    for name,digest in p['source_pins'].items():assert sha((k/name).read_bytes())==digest,name
    for name,digest in p['input_pins'].items():assert sha((ws/name).read_bytes())==digest,name
    for path,source,digest in changes:assert sha(source.read_bytes())==digest,path
    assert sha(proposal.read_bytes())==proposal_sha
    for name,digest in package['helpers'].items():assert sha((k/'artifacts'/name).read_bytes())==digest,name
    if case=='candidate001':
        a=read(k/'control001/physical-audit.json')
        assert candidate_permitted(a,read(k/'control001/physical-hive-audit.json'),read(k/'control001/restored-verification.json'))
        closure=read(k/'control001/closure.json');assert closure['closed'] and closure['scoped_display_passed']
        for name,digest in closure['evidence_pins'].items():assert sha((k/'control001'/name).read_bytes())==digest

def deploy_launch(keyboard_unplugged):
    assert keyboard_unplugged,'Persistent user-reported unplugged keyboard and authorized dashboard deployment'
    ready();assert all((k/'artifacts'/n).is_file() for n in package['helpers']);assert not record.exists();art.mkdir(parents=True,exist_ok=False)
    r=dict(scope=__doc__,case=case,namespace=namespace,created_utc=m.utc(),physical_result=True,
        physical_qualified=False,strict_qualification_passed=False,release_qualified=False,
        before_payloads={},before={},after={},launch_requested=False,startup_enabled=False,baseline_restored=False,
        keyboard_user_reported_unplugged=True,expected_baseline_error='Ft49 is retained as strict failure; no promotion')
    with m.connect() as f:
        m.owner(f);r['fixed_preflight']=fixed_checks(f)
        assert absence(f,'/F',namespace) and absence(f,'/F',rollback_dir)
        for path,p,digest in changes:
            data=None if path==xwnown and absence(f,'/F/winnt/system32','xwnown.dll') else m.get(f,path)
            r['before_payloads'][path]=None if data is None else preserve('before-'+p.name,data)
        for name,path in aux:r['before'][name]=preserve('before-'+name,m.get(f,path))
        for row in capture['files']:
            if row['path'].endswith(mutable_suffixes):continue
            r['before']['protected:'+row['path']]=preserve('before-protected-'+str(len(r['before'])),m.get(f,row['path']))
        save(r)
        rollback=art/'current-rollback211.zip';files=sorted(art.glob('before-*'))
        with zipfile.ZipFile(rollback,'x',compression=zipfile.ZIP_DEFLATED) as z:
            for p in files:z.writestr(p.name,p.read_bytes())
        with zipfile.ZipFile(rollback) as z:
            assert z.namelist()==[p.name for p in files] and all(z.read(p.name)==p.read_bytes() for p in files)
        r['rollback_sha256']=sha(rollback.read_bytes());r['rollback_entries']=len(files);save(r)
        f.mkd('/F/'+rollback_dir);m.put(f,'/F/'+rollback_dir+'/current-rollback211.zip',rollback.read_bytes())
        f.mkd('/F/'+namespace)
        m.put(f,'/F/'+namespace+'/runner.exe',(k/'artifacts/runner.exe').read_bytes())
        m.put(f,'/F/'+namespace+'/replay.exe',(k/'artifacts/replay.exe').read_bytes())
        m.put(f,'/F/'+namespace+'/wizard.exe',(k/'artifacts/wizard.exe').read_bytes())
        try:
            for path,p,_ in changes:m.put(f,path,p.read_bytes())
            m.put(f,system,proposal.read_bytes())
            m.put(f,startup,test_startup);r['startup_enabled']=True;save(r)
        except Exception as exc:
            r['prelaunch_failure']=repr(exc);save(r);restore(f,r);raise
        r.update(launch_requested=True,launch_utc=m.utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save(r)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=type(exc).__name__
        save(r);print('Single physical202 '+case+' requested; never repeat',flush=True)

def collect():
    r=read(record);assert r['launch_requested'] and not r.get('collected_utc') and not r.get('collection_failure'),'Never recollect a restored partial failure'
    with m.connect() as f:
        m.owner(f)
        m.put(f,startup,(art/'before-startup.cmd').read_bytes());r['startup_enabled']=False;save(r)
        paths=[('attempt.log','/F/'+namespace+'/attempt.log'),('wizard201.log','/F/'+namespace+'/wizard201.log'),('wizard.exe','/F/'+namespace+'/wizard.exe'),('runner.exe','/F/'+namespace+'/runner.exe'),('replay.exe','/F/'+namespace+'/replay.exe'),
            ('setup-before.log','/F/'+namespace+'/setup-before.log'),('setup-after.log','/F/'+namespace+'/setup-after.log'),
            *[('sample%d'%i,'/F/'+namespace+'/sample%d/gdi-baseline.txt'%i) for i in range(5)],*aux,
            *[(p.rsplit('/',1)[1],p) for p,_,_ in changes],
            *[('protected:'+row['path'],row['path']) for row in capture['files'] if not row['path'].endswith(mutable_suffixes)]]
        try:
            for name,path in paths:
                if name in r['after']:
                    row=r['after'][name]
                    if row:assert sha((ws/row['path']).read_bytes())==row['sha256']
                    continue
                data=m.get(f,path,optional=name in ['attempt.log','wizard201.log','setup-before.log','setup-after.log'] or name.startswith('sample'))
                filename='after-protected-'+str(len(r['after'])) if name.startswith('protected:') else 'after-'+name
                r['after'][name]=None if data is None else preserve(filename,data);save(r)
            r['collected_utc']=m.utc();save(r)
        except Exception as exc:
            r['collection_failure']=repr(exc);save(r);raise
        finally:
            restore(f,r)
        print('Startup restored first; evidence preserved; original display/SYSTEM restored',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['deploy-launch','collect','rollback']);p.add_argument('case',choices=['control001','candidate001']);p.add_argument('--keyboard-unplugged',action='store_true');a=p.parse_args()
    if a.action=='deploy-launch':deploy_launch(a.keyboard_unplugged)
    elif a.action=='collect':collect()
    else:
        r=read(record);assert not r.get('baseline_restored')
        with m.connect() as f:m.owner(f);restore(f,r)
