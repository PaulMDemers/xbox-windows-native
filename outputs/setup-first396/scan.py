"""One existing read-only E allocation scanner per unique case/boundary; outputs on F."""
import sys,time,json,subprocess
from pathlib import Path
from physical import K,read,connect,get,put,names,sha,utc,write_json,pins
case,phase,action=sys.argv[1:];assert case in ['control001','candidate001'] and phase in ['before','after'] and action in ['launch','observe','collect']
out=K/case/(phase+'-scan');record=out/'trial.json';remote='/F/Applications/XWNFatx396'+case+phase
payload=Path('E:/xwn341/build001/bin/default.xbe').read_bytes();assert sha(payload)==read(K.parent/'stock-scan341/build001.json')['outputs']['default.xbe']['sha256']
def launch():
    pins();assert read(K/case/'before.json')['completed']
    if phase=='after':assert read(K/case/'collection.json')['completed'] and read(K/case/'collection.json')['driver_restored']
    assert not out.exists();out.mkdir();r=dict(launch_requested=False,read_partition='E',output_volume='F',console_C_accessed=False,remote=remote,payload_sha256=sha(payload));write_json(record,r)
    with connect() as f:
        assert remote.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/F/Applications')}
        f.mkd(remote);put(f,remote+'/default.xbe',payload)
        r.update(launch_requested=True,launch_utc=utc(),command='SITE EXEC '+remote[1].upper()+':'+remote[2:].replace('/','\\')+'\\default.xbe');write_json(record,r);f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as e:r['reply_uncertain']=repr(e)
        write_json(record,r)
    print('One read-only E scan launched',case,phase,flush=True)
def observe():
    assert read(record)['launch_requested'] and not (out/'return.json').exists();r=dict(returned=False,offline=False,samples=[]);deadline=time.monotonic()+300
    while time.monotonic()<deadline:
        row=dict(utc=utc(),dashboard=False)
        try:
            with connect(timeout=3) as f:
                row['dashboard']=True;b=get(f,remote+'/snapshot.txt',optional=True);row['completed_report']=bool(b and b'SNAPSHOT_COMPLETE success=1 ' in b)
        except Exception as e:row['error']=type(e).__name__;r['offline']=True
        r['samples'].append(row);r['returned']=row['dashboard'] and row.get('completed_report',False);write_json(out/'return.json',r)
        if r['returned']:break
        time.sleep(3)
    r['closed']=True;write_json(out/'return.json',r);print('Read-only E scan returned',r['returned'],flush=True)
def collect():
    r=read(record);assert r['launch_requested'] and not r.get('collected');folder=Path('E:/xwn396')/(case+'-'+phase+'-scan');assert not folder.exists();folder.mkdir()
    with connect() as f:
        assert get(f,remote+'/default.xbe')==payload;r['files']={}
        for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            b=get(f,remote+'/'+name);(folder/name).write_bytes(b);r['files'][name]=dict(bytes=len(b),sha256=sha(b))
    assert b'SNAPSHOT_COMPLETE success=1 ' in (folder/'snapshot.txt').read_bytes()
    dest=K/case/('before-allocation.json' if phase=='before' else 'allocation.json');assert not dest.exists()
    subprocess.run([sys.executable,str(K.parent/'hd-phase-runtime346/analyze-allocation002.py'),'--capture',str(folder),'--output',str(dest)],check=True)
    r.update(collected=True,private=str(folder),collected_utc=utc(),allocation_sha256=sha(dest.read_bytes()));write_json(record,r)
    print('Read-only E scan collected and analyzed',case,phase,flush=True)
globals()[action]()
