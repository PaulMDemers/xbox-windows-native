"""One bounded native Windows audio trial per unique case; preserve failures."""
import sys,time
from common001 import *

assert len(sys.argv)==3 and sys.argv[1] in ['install001','playback001'] and sys.argv[2] in ['launch','observe','collect']
case,action=sys.argv[1:];out=k/case;record=out/'trial.json';art=k/'artifacts'/case
remote='/F/'+('xwnaC01i' if case=='install001' else 'xwnaC01p')
windows='C:\\'+remote.rsplit('/',1)[1]+'\\runner.exe'
test_startup=('@echo off\r\n'+windows+'\r\nexit\r\n').encode()
def save_trial(r):save(record,r)
def launch():
    pins();baseline_scan=read(k/'baseline001/allocation.json');assert baseline_scan['allocation_consistent'] and not baseline_scan['errors'] and not baseline_scan['orphan_cluster_count'];assert not out.exists() and not art.exists(),'Never repeat a trial or uncertain launch'
    assert read(k/'before-audit002.json')['passed'] and read(k/'providers001.json')['passed']
    if case=='playback001':assert read(k/'install001/audit.json')['scoped_installation_passed']
    if case=='install001':
        state=read(k/'before-audit002.json')
        assert state['aci_device']['service']==['ac97xnt5'] and state['aci_device']['configflags']==0
        assert state['aci_service']['start']==3 and state['aci_service']['type']==1
        assert state['aci_service']['imagepath'][0].lower()=='system32\\drivers\\ac97xnt5.sys'
        assert sha(incoming('/F/winnt/system32/drivers/ac97xnt5.sys'))=='9cccf729317efb34b1350c12ca2cc9b285fa57a8746147b93632bb1cce177efa'
    root=helpers();payload=root/('install' if case=='install001' else 'verify')
    out.mkdir();art.mkdir(parents=True)
    r=dict(case=case,physical_result=True,created_utc=utc(),launch_requested=False,startup_enabled=False,remote=remote,payloads=[],writes=[],physical_qualified=False,keyboard_user_reported_always_unplugged=True)
    save_trial(r)
    with connect() as f:
        r['protected_preflight']=check_fixed(f);assert get(f,startup)==incoming(startup)
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/F')},'Preserve old remote namespace'
        if case=='install001':
            for name in ['system','software','sam','security','default']:
                p='/F/winnt/system32/config/'+name;assert get(f,p)==incoming(p),'Incoming registry drift'
            assert get(f,'/F/winnt/system32/drivers/ac97xnt5.sys')==incoming('/F/winnt/system32/drivers/ac97xnt5.sys')
        else:
            prior=read(k/'install001/collection.json')
            for name in ['system','software','sam','security','default']:
                p='/F/winnt/system32/config/'+name
                expected=next(v['sha256'] for n,v in prior['files'].items() if n.lower()==p.lower())
                assert sha(get(f,p))==expected,'Post-install registry drift'
        save_trial(r)
        try:
            r['writes'].append(dict(action='mkdir',path=remote));save_trial(r);f.mkd(remote)
            for p in sorted(payload.iterdir()):
                assert p.is_file();data=p.read_bytes();path=remote+'/'+p.name
                r['writes'].append(dict(action='put',path=path,sha256=sha(data)));save_trial(r)
                put(f,path,data);r['payloads'].append(dict(path=path,sha256=sha(data),bytes=len(data),readback_verified=True));save_trial(r)
            if case=='install001':
                # Same safe-unload starting condition as the genuine install001 emulator trial.
                path='/F/winnt/system32/drivers/ac97xnt5.sys';data=(payload/'xwnaci207.sys').read_bytes()
                assert sha(data)=='c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75'
                r['writes'].append(dict(action='reviewed-legacy-bootstrap',path=path,original_sha256=sha(incoming(path)),sha256=sha(data),offline_binding_edit=False));save_trial(r)
                put(f,path,data);r['legacy_bootstrap_readback_verified']=True;save_trial(r)
            r['writes'].append(dict(action='replace-startup',path=startup,sha256=sha(test_startup)));save_trial(r)
            put(f,startup,test_startup);r['startup_enabled']=True;save_trial(r)
            r['protected_staged']=check_fixed(f);save_trial(r)
        except BaseException as exc:
            r['prelaunch_error_type']=type(exc).__name__;save_trial(r)
            put(f,startup,incoming(startup))
            if case=='install001':put(f,'/F/winnt/system32/drivers/ac97xnt5.sys',incoming('/F/winnt/system32/drivers/ac97xnt5.sys'))
            r.update(startup_enabled=False,prelaunch_startup_restored=True,prelaunch_legacy_restored=True);save_trial(r);raise
        r.update(launch_requested=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save_trial(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
        save_trial(r);print('Single '+case+' launch recorded; never relaunch',flush=True)
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
        logs=['install207.log','install-runner207.log','wizard201.log'] if case=='install001' else ['state207.log','audio207.log','runner207.log','wizard201.log']
        for name in logs:
            data=get(f,remote+'/'+name,optional=True)
            r['files'][remote+'/'+name]=None if data is None else keep(art,remote+'/'+name,data);save(dest,r)
        for root in ['/F/winnt/inf','/F/winnt/system32/config','/F/winnt/system32/drivers']:
            r['inventories'][root]=names(f,root);save(dest,r)
        paths=list(fixed())+[startup,'/F/winnt/setupapi.log','/F/winnt/system32/xwn-video-trace.bin','/F/winnt/system32/config/sysevent.evt','/F/winnt/system32/config/appevent.evt']
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
        r['protected_files_unchanged']=all(r['files'][p]['sha256']==h for p,h in fixed().items())
        r.update(completed=True,completed_utc=utc(),dashboard_available=True);save(dest,r)
    print('Evidence collected and normal startup restored; qualification pending',flush=True)
globals()[action]()
