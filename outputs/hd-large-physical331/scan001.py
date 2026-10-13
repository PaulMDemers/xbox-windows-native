"""One validated read-only F allocation scan per physical case, with E-only reports."""
import sys,time
from common001 import *
assert len(sys.argv)==3 and sys.argv[1] in ['physical001'] and sys.argv[2] in ['launch','observe','collect']
case,action=sys.argv[1:];out=k/case;record=out/'scan.json'
remote='/E/Applications/'+dict(physical001='XWNHD331scan')[case]
source=canonical/'outputs/native-windows-fatx-preflight/artifacts/default.xbe'
payload=source.read_bytes();assert sha(payload)=='c6c878447d2a5ace95fced0e6d7c819fd5271e665cd0fc8efe886c5232cbdf05'
def launch():
    pins();assert not record.exists(),'Never repeat scan'
    assert read(out/'collection.json')['completed'] and read(out/'collection.json')['baseline_restored']
    out.mkdir(exist_ok=True)
    with connect() as f:
        assert get(f,startup)==incoming(startup);check_fixed(f)
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E/Applications')}
        r=dict(case=case,scope=__doc__,remote=remote,payload_sha256=sha(payload),launch_requested=False,created_utc=utc());save(record,r)
        f.mkd(remote);put(f,remote+'/default.xbe',payload)
        r.update(launch_requested=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\'+remote.rsplit('/',1)[1]+'\\default.xbe');save(record,r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
        save(record,r);print('One read-only allocation scan launched: '+case,flush=True)
def observe():
    ticket();r=read(record);assert r['launch_requested'] and not (out/'scan-return.json').exists()
    result=dict(case=case,dashboard_return=False,offline_observed=False,samples=[],new_launches=0);deadline=time.monotonic()+300
    while time.monotonic()<deadline:
        row=dict(utc=utc(),dashboard=False,fresh_complete=False)
        try:
            with connect(timeout=3) as f:
                row['dashboard']=True;data=get(f,remote+'/snapshot.txt',optional=True)
                row['fresh_complete']=bool(data and b'SNAPSHOT_COMPLETE success=1 ' in data)
        except Exception as exc:row['error_type']=type(exc).__name__;result['offline_observed']=True
        result['samples'].append(row);result['dashboard_return']=row['dashboard'] and (result['offline_observed'] or row['fresh_complete'])
        save(out/'scan-return.json',result)
        if result['dashboard_return']:break
        time.sleep(min(5,max(0,deadline-time.monotonic())))
    result.update(closed=True,closed_utc=utc());save(out/'scan-return.json',result)
    print('Scan observation closed: dashboard_return='+str(result['dashboard_return']),flush=True)
def collect():
    pins();r=read(record);assert r['launch_requested'] and not r.get('collected')
    folder=k/'artifacts'/case/'allocation';assert not folder.exists();folder.mkdir(parents=True)
    with connect() as f:
        assert get(f,startup)==incoming(startup);assert get(f,remote+'/default.xbe')==payload
        r['files']={}
        for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            data=get(f,remote+'/'+name);r['files'][name]=keep(folder,name,data)
        r['snapshot_complete']=b'SNAPSHOT_COMPLETE success=1 ' in (folder/'snapshot.txt').read_bytes()
        r.update(collected=True,collected_utc=utc(),dashboard_available=True);save(record,r)
    print('Read-only allocation metadata retained; analysis pending',flush=True)
globals()[action]()
