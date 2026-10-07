"""Single read-only raw C inventory; writes reports only inside its owned E app folder."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"fatx0101-physical"))
from physical import k,ws,connect,owner,get,put,save,sha,utc,missing,startup,baseline,candidate_sha,driver
k=Path(__file__).resolve().parent
remote='/E/Applications/XWNRawC001';record=k/'physical.json';out=k/'artifacts/physical'
p=argparse.ArgumentParser();p.add_argument('action',choices=['launch','collect']);a=p.parse_args()
trial=json.loads((k.parent/'fatx0101-physical/physical.json').read_text());assert trial.get('collected_utc') and not trial['startup_enabled']
pre=k;validation=json.loads((pre/'validation.json').read_text())
assert validation['passed'] and validation['no_C_overlay_writes']
xbe=(pre/'artifacts/default.xbe').read_bytes();assert sha(xbe)==validation['xbe_sha256']
marker=dict(project='xbox-windows-native',purpose='raw-c-readonly-capacity-inventory',xbe_sha256=sha(xbe))
with connect() as f:
    owner(f);assert sha(get(f,startup))==baseline['startup_sha256'];assert sha(get(f,driver))==candidate_sha
    if a.action=='launch':
        assert not record.exists(),'Never repeat a scan launch';missing(f,remote)
        r=dict(scope=__doc__,created_utc=utc(),remote=remote,owner=marker,launch_attempted=False);save(r,record)
        f.mkd(remote);put(f,remote+'/owner.json',json.dumps(marker).encode());put(f,remote+'/default.xbe',xbe)
        r.update(launch_attempted=True,launch_utc=utc(),command='SITE EXEC E:\\Applications\\XWNRawC001\\default.xbe');save(r,record)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as exc:r['reply_uncertain']=type(exc).__name__
        save(r,record);print('Read-only allocation scan launched once',flush=True)
    else:
        r=json.loads(record.read_text());assert r['launch_attempted'] and not r.get('collected_utc')
        assert json.loads(get(f,remote+'/owner.json'))==marker and sha(get(f,remote+'/default.xbe'))==sha(xbe)
        out.mkdir(parents=True,exist_ok=True);r['files']=[]
        for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            data=get(f,remote+'/'+name);path=out/name
            if path.exists():assert path.read_bytes()==data
            else:path.write_bytes(data)
            r['files'].append(dict(name=name,bytes=len(data),sha256=sha(data)))
        r.update(collected_utc=utc(),report=(out/'snapshot.txt').read_text())
        r['complete']='SNAPSHOT_COMPLETE success=1 ' in r['report'];save(r,record);assert r['complete']
        subprocess.run([sys.executable,str(pre/'analyze.py'),'--capture',str(out),'--output',str(k/'physical-allocation.json')],check=True)
