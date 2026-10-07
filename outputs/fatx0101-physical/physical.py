"""Single candidate0101 physical concurrency trial; preserve0098 and video0093."""
import argparse,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];art=k/'artifacts/physical';record=k/'physical.json'
spec=importlib.util.spec_from_file_location('prior_physical',k.parent/'fatx0098-soak3/physical.py')
oldmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(oldmod)
connect,owner,get,put,sha,utc,missing,passed=[getattr(oldmod,n) for n in ['connect','owner','get','put','sha','utc','missing','passed']]
startup,baseline,driver,expected=[getattr(oldmod,n) for n in ['startup','baseline','driver','expected']]
expected=dict(expected)
candidate_sha='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
kit=k.parent/'fatx-directory-order';directory='/F/xwn101a';results='/F/xwncc01'
test_startup=b'@echo off\r\nC:\\xwn101a\\probe.exe\r\nexit\r\n'
def save(r,path=record):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(path)
def preserve(name,data):
    art.mkdir(parents=True,exist_ok=True);p=art/name
    if p.exists():assert p.read_bytes()==data,'Evidence changed: '+name
    else:p.write_bytes(data)
    return dict(bytes=len(data),sha256=sha(data))
def checks(f,candidate=False):
    values=dict(expected)
    if candidate:values[driver]=candidate_sha
    return {p:dict(sha256=sha(get(f,p)),expected=h) for p,h in values.items()}
def eligible():
    e=json.loads((kit/'candidate-eligibility.json').read_text());assert e['eligible_for_controlled_hardware_trial'] and e['driver_sha256']==candidate_sha
    for p,h in e['evidence_sha256'].items():assert sha((k.parent/p).read_bytes())==h
    probe=(kit/'artifacts/probe.exe').read_bytes();review=json.loads((kit/'probe-review.json').read_text())
    assert review['passed'] and sha(probe)==review['probe_sha256']=='aca62d7200e9fb1936ea9c33a1538b96ad8bbeebfb2970b6bff4a689408b5a6d'
    candidate=(kit/'artifacts/xwnfatx.sys').read_bytes();assert sha(candidate)==candidate_sha
    return e,probe,candidate
def main(action):
    if action in ['check','deploy-launch']:e,probe,candidate=eligible()
    with connect() as f:
        owner(f)
        if action=='check':
            assert not (k/'preflight.json').exists()
            r=dict(scope='Read-only physical preflight; no writes or launch',utc=utc(),checks=checks(f),startup_sha256=sha(get(f,startup)))
            missing(f,directory);missing(f,results);r['unique_paths_absent']=[directory,results]
            r['passed']=passed(r['checks']) and r['startup_sha256']==baseline['startup_sha256'];save(r,k/'preflight.json');assert r['passed'];print('Preflight PASS: baseline, startup, ownership and unique paths')
        elif action=='deploy-launch':
            assert not record.exists(),'Never repeat deployment/launch'
            assert json.loads((k/'preflight.json').read_text())['passed']
            assert passed(checks(f));original=get(f,startup);assert sha(original)==baseline['startup_sha256'];missing(f,directory);missing(f,results)
            old=get(f,driver);assert sha(old)==expected[driver]
            r=dict(scope=__doc__,created_utc=utc(),launch_attempted=False,startup_enabled=False,candidate_sha256=candidate_sha,probe_sha256=sha(probe),preserved={},payloads=[],eligibility_sha256=sha((kit/'candidate-eligibility.json').read_bytes()),keyboard_readiness='Latest human Proceed accepted as readiness after keyboard-unplug request',result_directory=results)
            for name,data in [('before-startup.cmd',original),('before-xwnfatx.sys',old),('candidate-xwnfatx.sys',candidate),('probe.exe',probe),('before-trace.bin',get(f,'/F/winnt/system32/xwn-video-trace.bin')),('before-system.evt',get(f,'/F/winnt/system32/config/sysevent.evt')),('before-application.evt',get(f,'/F/winnt/system32/config/appevent.evt'))]:r['preserved'][name]=preserve(name,data)
            save(r)
            try:
                f.mkd(directory)
                for path,data in [(directory+'/rollback.sys',old),(directory+'/startup.cmd',original),(directory+'/probe.exe',probe),(driver,candidate)]:
                    put(f,path,data);r['payloads'].append(dict(path=path,bytes=len(data),sha256=sha(data)));save(r)
                assert passed(checks(f,True));put(f,startup,test_startup);r['startup_enabled']=True;save(r)
            except Exception as exc:
                r['prelaunch_error']=repr(exc);save(r)
                put(f,startup,original);put(f,driver,old);r.update(startup_enabled=False,prelaunch_rollback=True);save(r);raise
            r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save(r)
            try:r['reply']=f.sendcmd(r['command'])
            except Exception as exc:r['reply_uncertain']=type(exc).__name__
            save(r);print('Single launch recorded:',r.get('reply',r.get('reply_uncertain')),flush=True)
        else:
            r=json.loads(record.read_text());assert r['launch_attempted']
            original=(art/'before-startup.cmd').read_bytes();assert sha(original)==baseline['startup_sha256']
            assert get(f,startup) in [test_startup,original]
            put(f,startup,original);r.update(startup_enabled=False,startup_restored_utc=utc());save(r)
            if action=='collect':
                assert not r.get('collected_utc');r.setdefault('collected',{})
                files={'system.evt':'/F/winnt/system32/config/sysevent.evt','application.evt':'/F/winnt/system32/config/appevent.evt','trace.bin':'/F/winnt/system32/xwn-video-trace.bin','setupapi.log':'/F/winnt/setupapi.log'}
                files.update({n:results+'/'+n for n in ['probe.log','worker0.bin','worker1.bin','meta.bin','meta.tmp']})
                for name,path in files.items():
                    data=get(f,path,optional=name in ['probe.log','worker0.bin','worker1.bin','meta.bin','meta.tmp','setupapi.log'])
                    r['collected'][name]=preserve('after-'+name,data) if data is not None else None;save(r)
                r['candidate_checks']=checks(f,True);r['probe_unchanged']=sha(get(f,directory+'/probe.exe'))==r['probe_sha256']
                r['rollback_exact']=sha(get(f,directory+'/rollback.sys'))==expected[driver]
                r['collected_utc']=utc();save(r);print('Collected; normal startup restored first; qualification pending')
            elif action=='rollback':
                old=(art/'before-xwnfatx.sys').read_bytes();assert sha(old)==expected[driver]
                assert sha(get(f,driver)) in [candidate_sha,expected[driver]];put(f,driver,old)
                r.update(driver_rollback_utc=utc(),rollback_checks=checks(f));save(r);assert passed(r['rollback_checks']);print('Baseline0098 restored and verified; no launch')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','deploy-launch','collect','restore-startup','rollback']);main(p.parse_args().action)
