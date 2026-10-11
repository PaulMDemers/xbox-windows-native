"""Single combined hardware launch; preserve incoming bytes and restore normal startup first."""
import sys,time
from common001 import *
assert len(sys.argv)==2 and sys.argv[1] in ['launch','observe','collect']
action=sys.argv[1];case='combined001';out=k/case;record=out/'trial.json';art=k/'artifacts'/case
remote='/F/xwnd253';test_startup=b'@echo off\r\nC:\\xwnd253\\runner.exe /physical\r\nexit\r\n'
package=read(k/'package.json')
def save_trial(r):save(record,r)
def launch():
    pins();assert not out.exists() and not art.exists(),'Never repeat launch'
    a=read(canonical/'outputs/demo-physical252/install001/audit.json');assert a['scoped_installation_passed']
    assert read(k/'before-audit002.json')['aci_device']['service']==['xwnaci207']
    out.mkdir();art.mkdir(parents=True)
    r=dict(case=case,physical_result=True,created_utc=utc(),launch_requested=False,startup_enabled=False,remote=remote,payloads=[],writes=[],before_payloads={},physical_qualified=False)
    save_trial(r)
    with connect() as f:
        r['protected_preflight']=check_fixed(f);assert get(f,startup)==incoming(startup)
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/F')}
        for name in ['system','software','sam','security','default']:
            p='/F/winnt/system32/config/'+name;assert get(f,p)==incoming(p),'Post-audio registry drift'
        for row in package['video']:
            path=row['path'];data=get(f,path,optional=path.endswith('/xwnown.dll'))
            r['before_payloads'][path]=None if data is None else keep(art/'rollback',path,data)
        save_trial(r)
        try:
            r['writes'].append(dict(action='mkdir',path=remote));save_trial(r);f.mkd(remote)
            for row in package['helpers']:
                p=remote+'/'+row['name'];data=(k/'artifacts/payload'/row['name']).read_bytes();assert sha(data)==row['sha256']
                r['writes'].append(dict(path=p,sha256=sha(data)));save_trial(r);put(f,p,data)
                r['payloads'].append(dict(path=p,sha256=sha(data)));save_trial(r)
            for row in package['video']:
                path=row['path'];data=(k/'artifacts/payload'/row['name']).read_bytes();assert sha(data)==row['sha256']
                r['writes'].append(dict(path=path,sha256=sha(data)));save_trial(r);put(f,path,data)
            data=(k/'artifacts/proposed-system').read_bytes();assert sha(data)==package['proposed_system_sha256']
            path='/F/winnt/system32/config/system';r['writes'].append(dict(path=path,sha256=sha(data)));save_trial(r);put(f,path,data)
            r['writes'].append(dict(path=startup,sha256=sha(test_startup)));save_trial(r);put(f,startup,test_startup)
            r['startup_enabled']=True;r['protected_staged']=check_fixed(f,staged=True);save_trial(r)
        except BaseException as exc:
            r['prelaunch_error_type']=type(exc).__name__;save_trial(r);put(f,startup,incoming(startup))
            put(f,'/F/winnt/system32/config/system',incoming('/F/winnt/system32/config/system'))
            for path,row in r['before_payloads'].items():
                if row is None:
                    current=get(f,path,optional=True)
                    if current is not None:
                        assert sha(current)==next(v['sha256'] for v in package['video'] if v['path']==path)
                        f.delete(path)
                else:
                    data=(art/'rollback'/path.lstrip('/')).read_bytes();assert sha(data)==row['sha256'];put(f,path,data)
            r.update(startup_enabled=False,prelaunch_rollback=True);save_trial(r);raise
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save_trial(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
        save_trial(r);print('Single combined253 launch recorded; never relaunch',flush=True)

def observe():
    ticket();r=read(record);assert r['launch_requested'] and not (out/'return.json').exists()
    result=dict(case=case,launch_utc=r['launch_utc'],dashboard_return=False,offline_observed=False,samples=[],new_launches=0,observer_pid=os.getpid())
    deadline=time.monotonic()+600
    while time.monotonic()<deadline:
        sample=dict(utc=utc(),dashboard=False)
        try:
            with connect(timeout=3) as f:sample['dashboard']=True
        except Exception as exc:sample['error_type']=type(exc).__name__;result['offline_observed']=True
        result['samples'].append(sample)
        result['dashboard_return']=sample['dashboard'] and result['offline_observed'];save(out/'return.json',result)
        if result['dashboard_return']:break
        time.sleep(min(5,max(0,deadline-time.monotonic())))
    result.update(closed=True,closed_utc=utc());save(out/'return.json',result)
    print('Observation closed: dashboard_return='+str(result['dashboard_return']),flush=True)

def collect():
    pins();trial=read(record);assert trial['launch_requested'] and not (out/'collection.json').exists()
    dest=out/'collection.json';r=dict(case=case,physical_result=True,files={},inventories={},startup_restored=False,completed=False,created_utc=utc())
    save(dest,r)
    with connect() as f:
        current=get(f,startup);assert current in [incoming(startup),test_startup],'Unexpected startup'
        put(f,startup,incoming(startup));r['startup_restored']=True;trial['startup_enabled']=False;save_trial(trial);save(dest,r)
        logs=['attempt.log','wizard201.log','setup-before.log','setup-after.log','state207.log','audio207.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]
        for name in logs:
            data=get(f,remote+'/'+name,optional=True)
            r['files'][remote+'/'+name]=None if data is None else keep(art,remote+'/'+name,data);save(dest,r)
        for root in ['/F/winnt/inf','/F/winnt/system32/config','/F/winnt/system32/drivers']:
            r['inventories'][root]=names(f,root);save(dest,r)
        paths=list(fixed())+[v['path'] for v in package['video']]+[startup,'/F/winnt/setupapi.log','/F/winnt/system32/xwn-video-trace.bin','/F/winnt/system32/config/sysevent.evt','/F/winnt/system32/config/appevent.evt']
        for name,row in r['inventories']['/F/winnt/system32/config'].items():
            if not row['directory'] and name.lower().split('.')[0] in ['system','software','sam','security','default']:paths.append('/F/winnt/system32/config/'+name)
        for name,row in r['inventories']['/F/winnt/inf'].items():
            if not row['directory']:paths.append('/F/winnt/inf/'+name)
        for name,row in r['inventories']['/F/winnt/system32/drivers'].items():
            if not row['directory'] and any(s in name.lower() for s in ['ac97','xwnaci','wdmaud','portcls','sysaudio','swmidi']):paths.append('/F/winnt/system32/drivers/'+name)
        for path in dict.fromkeys(paths):
            data=get(f,path);r['files'][path]=keep(art,path,data)
            if '/config/' in path:assert get(f,path)==data,'Cold file changed during collection'
            save(dest,r)
        for row in trial['payloads']:assert sha(get(f,row['path']))==row['sha256'],'Payload changed'
        expected=dict(fixed());expected.update({v['path']:v['sha256'] for v in package['video']})
        r['protected_files_unchanged']=all(r['files'][p]['sha256']==h for p,h in expected.items())
        r.update(completed=True,completed_utc=utc(),dashboard_available=True);save(dest,r)
    print('Evidence collected and normal startup restored; qualification pending',flush=True)

globals()[action]()
