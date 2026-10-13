"""One read-only E allocation scan per unique phase; new output files live only on F."""
import json,sys,time,os
from pathlib import Path
K=Path(__file__).resolve().parent;phase,action=sys.argv[1:];assert phase in ['before','after'] and action in ['launch','observe','collect']
sys.path.insert(0,str(K.parent/'demo-audio-level256'));from common001 import connect,get,put,names,sha,utc,ticket
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
out=K/phase;record=out/'trial.json';remote='/F/Applications/XWNStock341'+phase
read=lambda p:json.loads(p.read_text());payload=Path('E:/xwn341/build001/bin/default.xbe').read_bytes()
for path,digest in read(K/'frozen.json').items():assert sha((K.parents[1]/path).read_bytes())==digest,path
assert sha(payload)==read(K/'build001.json')['outputs']['default.xbe']['sha256'] and read(K/'host002.json')['passed']
def launch():
    assert read(K.parent/'stock-stage340/physical001.json')['complete']
    assert not out.exists();out.mkdir()
    if phase=='after':assert read(K.parent/'stock-boot342/physical001/collection.json')['completed']
    with connect() as f:
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/F/Applications')}
        r=dict(launch_requested=False,read_partition='E',output_volume='F',console_c_accessed=False,remote=remote,payload_sha256=sha(payload),started_utc=utc());write_json(record,r)
        f.mkd(remote);put(f,remote+'/default.xbe',payload)
        r.update(launch_requested=True,launch_utc=utc(),command='SITE EXEC F:\\Applications\\XWNStock341'+phase+'\\default.xbe');write_json(record,r)
        assert r['command']=='SITE EXEC F:\\Applications\\XWNStock341'+phase+'\\default.xbe'
        f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=repr(exc)
        write_json(record,r)
    print('One E allocation scan launched; never repeat',phase,flush=True)
def observe():
    assert read(record)['launch_requested'] and not (out/'return.json').exists()
    r=dict(returned=False,offline=False,samples=[]);deadline=time.monotonic()+300
    while time.monotonic()<deadline:
        row=dict(utc=utc(),dashboard=False)
        try:
            with connect(timeout=3) as f:
                row['dashboard']=True;b=get(f,remote+'/snapshot.txt',optional=True);row['completed_report']=bool(b and b'SNAPSHOT_COMPLETE success=1 ' in b)
        except Exception as exc:row['error']=type(exc).__name__;r['offline']=True
        r['samples'].append(row);r['returned']=row['dashboard'] and (r['offline'] or row.get('completed_report',False));write_json(out/'return.json',r)
        if r['returned']:break
        time.sleep(3)
    r['closed']=True;write_json(out/'return.json',r);print('Scan observer closed',r['returned'],flush=True)
def collect():
    r=read(record);assert r['launch_requested'] and not r.get('collected');folder=Path('E:/xwn341')/('physical-'+phase);assert not folder.exists();folder.mkdir()
    with connect() as f:
        assert get(f,remote+'/default.xbe')==payload;r['files']={}
        for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            b=get(f,remote+'/'+name);(folder/name).write_bytes(b);r['files'][name]=dict(bytes=len(b),sha256=sha(b))
        assert b'SNAPSHOT_COMPLETE success=1 ' in (folder/'snapshot.txt').read_bytes()
    r.update(collected=True,private=str(folder),collected_utc=utc());write_json(record,r);print('Collected E allocation capture',phase,flush=True)
globals()[action]()
