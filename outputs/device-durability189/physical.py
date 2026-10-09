"""Unique post188 baseline durability observer; unchanged drivers/policy and manual restart."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1]
spec=importlib.util.spec_from_file_location('ftp_helpers',k.parent/'fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
record=k/'physical.json';art=k/'artifacts/physical';remote='/F/xwnobs189a'
startup=m.startup;test_startup=b'@echo off\r\nC:\\xwnobs189a\\observer.exe\r\nexit\r\n'
parent=k.parent/'device-observation188'
previous=read(parent/'physical.json')
fixed=previous['after_checks']
expected_startup=previous['after']['startup.cmd']['sha256']
expected_system=previous['after']['system']['sha256']
probe_path=parent/'artifacts/build003/observer.exe'
aux=[('startup.cmd',startup)]+[(n,'/F/winnt/system32/config/'+n) for n in ['system','software','default','sam','security','sysevent.evt','appevent.evt']]+[('setupapi.log','/F/winnt/setupapi.log'),('trace.bin','/F/winnt/system32/xwn-video-trace.bin')]
def save(r):write_json(record,r)
def preserve(name,data):
    p=art/name
    if p.exists():assert p.read_bytes()==data,'Preserved bytes changed: '+name
    else:p.write_bytes(data)
    return dict(path=p.relative_to(ws).as_posix(),bytes=len(data),sha256=sha(data))
def checks(f):
    rows=[]
    for v in fixed:
        actual=sha(m.get(f,v['path']));assert actual==v['sha256'],'Baseline drift: '+v['path']
        rows.append(dict(path=v['path'],sha256=actual))
    return rows
def ready():
    import shutil
    r=read(k/'ready.json');assert r['prepared'] and not r['physical_qualified']
    for name,digest in r['pins'].items():assert sha((ws/name).read_bytes())==digest,name
    assert read(parent/'physical-closure.json')['closed']
    assert read(parent/'physical-audit.json')['diagnostic_usable']
    assert previous.get('collected_utc') and not previous['startup_enabled']
    assert shutil.disk_usage(ws).free >= 20*1024**3,'Preserve20GiB launch guard'

def launch(keyboard_unplugged):
    assert keyboard_unplugged,'Require current dashboard/unplugged keyboard report'
    ready();assert not record.exists(),'Never repeat uncertain launch'
    art.mkdir(parents=True,exist_ok=False)
    probe=probe_path.read_bytes();assert sha(probe)==read(parent/'build-review.json')['binary_sha256']
    with m.connect() as f:
        m.owner(f);before=checks(f);m.missing(f,remote)
        original=m.get(f,startup);assert sha(original)==expected_startup
        system=m.get(f,'/F/winnt/system32/config/system');assert sha(system)==expected_system
        r=dict(scope=__doc__,created_utc=m.utc(),launch_requested=False,startup_enabled=False,physical_qualified=False,
            keyboard_user_reported_unplugged=True,probe_sha256=sha(probe),before_checks=before,before={},after={})
        for name,path in aux:r['before'][name]=preserve('before-'+name,m.get(f,path))
        for i,row in enumerate(fixed):r['before'][row['path']]=preserve('before-protected-'+str(i),m.get(f,row['path']))
        save(r)
        try:
            f.mkd(remote);m.put(f,remote+'/observer.exe',probe);m.put(f,remote+'/normal-startup.cmd',original)
            m.put(f,startup,test_startup);r['startup_enabled']=True;save(r)
        except Exception as exc:
            r['staging_failure']=repr(exc);save(r);m.put(f,startup,original);r['startup_enabled']=False;save(r);raise
        r.update(launch_requested=True,launch_utc=m.utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe');save(r)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=type(exc).__name__
        save(r);print('Single189 baseline durability observer launch requested; no automatic restart or UI action',flush=True)
def collect():
    r=read(record);assert r['launch_requested'] and not r.get('collected_utc') and not r.get('collection_failure')
    original=(art/'before-startup.cmd').read_bytes();assert sha(original)==r['before']['startup.cmd']['sha256']
    with m.connect() as f:
        m.owner(f)
        # FIRST restore startup, preserving registry and device changes as evidence.
        assert m.get(f,startup) in [test_startup,original]
        m.put(f,startup,original);r['startup_enabled']=False;save(r)
        try:
            for name,path in [('observer.log',remote+'/observer.log'),*aux,*[(v['path'],v['path']) for v in fixed]]:
                data=m.get(f,path,optional=name=='observer.log')
                file='after-protected-'+str(len(r['after'])) if name.startswith('/') else 'after-'+name
                r['after'][name]=None if data is None else preserve(file,data);save(r)
            r['after_checks']=checks(f);r['helper_exact']=sha(m.get(f,remote+'/observer.exe'))==r['probe_sha256']
            r['startup_backup_exact']=m.get(f,remote+'/normal-startup.cmd')==original
            r['collected_utc']=m.utc();save(r)
        except Exception as exc:r['collection_failure']=repr(exc);save(r);raise
        print('189 normal startup restored FIRST; observer/event/registry evidence preserved',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','collect']);p.add_argument('--keyboard-unplugged',action='store_true');a=p.parse_args()
    if a.action=='launch':launch(a.keyboard_unplugged)
    else:collect()
