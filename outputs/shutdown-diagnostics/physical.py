"""One bounded hardware observation, unchanged drivers and no device-state edits."""
import argparse,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('baseline',k.parent/'fatx0098-soak3/physical.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
record=k/'physical.json';art=k/'artifacts/physical';remote='/F/xwnsd01'
test=b'@echo off\r\nC:\\xwnsd01\\probe.exe\r\nexit\r\n'
def preserve(name,data):
    art.mkdir(parents=True,exist_ok=True);p=art/name
    if p.exists():assert p.read_bytes()==data
    else:p.write_bytes(data)
    return dict(bytes=len(data),sha256=b.sha(data))
def save(r):b.save(r,record)
p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','collect']);a=p.parse_args()
with b.connect() as f:
    b.owner(f)
    if a.action=='launch':
        assert not record.exists(),'Never repeat an uncertain launch'
        audit=json.loads((k/'001/audit.json').read_text());assert audit['strict_run_passed'] and audit['completed']
        review=json.loads((k/'probe-review.json').read_text());probe=(k/'artifacts/probe.exe').read_bytes()
        assert review['passed'] and b.sha(probe)==review['probe_sha256']
        assert any(v['path']=='xwnsd01/probe.exe' and v['sha256']==b.sha(probe) and v['matched'] for v in audit['payloads'])
        assert b.passed(b.checks(f));original=b.get(f,b.startup);assert b.sha(original)==b.baseline['startup_sha256'];b.missing(f,remote)
        r=dict(scope=__doc__,created_utc=b.utc(),probe_sha256=b.sha(probe),emulator_audit_sha256=b.sha((k/'001/audit.json').read_bytes()),launch_attempted=False,startup_enabled=False,preserved={})
        for name,path in [('before-startup.cmd',b.startup),('before-system.evt','/F/winnt/system32/config/sysevent.evt'),('before-application.evt','/F/winnt/system32/config/appevent.evt'),('before-setupapi.log','/F/winnt/setupapi.log')]:r['preserved'][name]=preserve(name,b.get(f,path))
        save(r)
        try:
            f.mkd(remote);b.put(f,remote+'/probe.exe',probe);b.put(f,remote+'/startup.cmd',original)
            b.put(f,b.startup,test);r['startup_enabled']=True;save(r)
        except Exception:
            b.put(f,b.startup,original);r['startup_enabled']=False;r['staging_failed']=True;save(r);raise
        r.update(launch_attempted=True,launch_utc=b.utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe');save(r)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=type(exc).__name__
        save(r);print('Single diagnostic launch recorded',r.get('reply',r.get('reply_uncertain')))
    else:
        r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc')
        original=(art/'before-startup.cmd').read_bytes();assert b.sha(original)==b.baseline['startup_sha256']
        assert b.get(f,b.startup) in [test,original];b.put(f,b.startup,original);r['startup_enabled']=False;save(r)
        r['collected']={}
        for name,path in [('probe.log',remote+'/probe.log'),('system.evt','/F/winnt/system32/config/sysevent.evt'),('application.evt','/F/winnt/system32/config/appevent.evt'),('setupapi.log','/F/winnt/setupapi.log')]:
            data=b.get(f,path,optional=name=='probe.log');r['collected'][name]=None if data is None else preserve('after-'+name,data);save(r)
        r['baseline_checks']=b.checks(f);r['probe_exact']=b.sha(b.get(f,remote+'/probe.exe'))==r['probe_sha256'];r['collected_utc']=b.utc();save(r)
        print('Normal startup restored; diagnostic evidence collected')
