"""One owned E application; query E/F, no C access or Windows changes."""
import ftplib,hashlib,json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'demo-audio-level256'));from common001 import connect,names,get,put,ticket,utc
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
out=K/'physical001';assert not out.exists();out.mkdir()
dest=out/'trial.json';r=dict(physical_access=True,console_c_accessed=False,windows_changed=False,launch_requested=False,writes=[],complete=False)
save=lambda:write_json(dest,r)
review=json.loads((K/'capacity-emu003/query-review.json').read_text());assert review['e_query_verified'] and review['host_orderly']
build=json.loads((K/'capacity-build002.json').read_text());assert build['compiled'] and build['sdk_unchanged']
payload=Path('E:/xwn333/capacity-build002/bin/default.xbe').read_bytes();assert hashlib.sha256(payload).hexdigest()==build['outputs']['default.xbe']['sha256']
folder='/E/Applications/XWNCapacity333';r['payload_sha256']=hashlib.sha256(payload).hexdigest();save()
try:
    ticket()
    with connect(timeout=8) as f:
        assert 'xwncapacity333' not in {n.lower() for n in names(f,'/E/Applications')},'Owned namespace must be new'
        r['mkdir_requested']=folder;save();f.mkd(folder)
        r['writes'].append(folder+'/default.xbe');save();put(f,folder+'/default.xbe',payload)
        assert set(names(f,folder))=={'default.xbe'}
        r.update(payload_readback=True,launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNCapacity333\default.xbe');save()
        try:r['reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as e:r['reply_uncertain']=type(e).__name__
        save()
    deadline=time.monotonic()+100
    while time.monotonic()<deadline:
        time.sleep(2)
        try:
            with connect(timeout=3) as f:
                report=get(f,folder+'/capacity.txt',optional=True)
                if report is None:continue
                assert len(report)<1024 and report.endswith(b'COMPLETE 333\r\n')
                assert get(f,folder+'/default.xbe')==payload
                (out/'capacity.txt').write_bytes(report)
                rows=report.decode('ascii').splitlines();assert len(rows)==4 and rows[0]=='XWN-CAPACITY-333'
                r['queries']=[]
                for row,pid in zip(rows[1:3],[1,6]):
                    x=row.split();assert x[0]=='SPACE' and len(x)==7
                    ident,start,length,unit,total,free=map(int,x[1:]);assert ident==pid and 0<=free<=total<=length and unit>0
                    r['queries'].append(dict(partition=ident,start=start,length=length,cluster_bytes=unit,total_bytes=total,free_bytes=free))
                assert r['queries'][0]['start']==5633024*512 and r['queries'][0]['length']==10000048*512
                r.update(complete=True,dashboard_return_utc=utc(),report_sha256=hashlib.sha256(report).hexdigest());save();break
        except (OSError,EOFError,ftplib.Error) as e:r['last_poll_error']=type(e).__name__;save()
    assert r['complete'],'No completed report; inspect state, never relaunch'
except BaseException as e:r['error']=repr(e);save();raise
finally:save();print(json.dumps(r,indent=2))
