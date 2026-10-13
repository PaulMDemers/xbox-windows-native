"""Capture current F Windows roots privately for isolated E deployment; no writes."""
import json,hashlib,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn337/capture001');dest=K/'capture001.json'
assert not P.exists() and not dest.exists()
sys.path.insert(0,str(K.parent/'demo-audio-level256'));from common001 import connect,get,names,sha,utc,ticket
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
summary=json.loads((K.parent/'stock-drive333/windows-inventory001.json').read_text());listing=Path(summary['private_listing'])
assert sha(listing.read_bytes())==summary['private_listing_sha256']
items=json.loads(listing.read_text())['entries'];assert summary['listing_complete']
P.mkdir(parents=True);r=dict(complete=False,physical_writes=False,console_c_accessed=False,started_utc=utc(),files={},directories=[],private=str(P),listing_sha256=summary['private_listing_sha256'])
save=lambda:write_json(dest,r)
deadline=time.monotonic()+1200;save()
try:
    with connect(timeout=15) as f:
        assert not {n.lower() for n in names(f,'/E')} & {'winnt','documents and settings','program files'}
        for path,meta in items.items():
            assert any(path.startswith(root+'/') for root in ['/F/winnt','/F/documents and settings','/F/program files'])
            assert time.monotonic()<deadline
            local=P/path.lstrip('/');assert local.resolve().is_relative_to(P.resolve())
            if meta['directory']:local.mkdir(parents=True,exist_ok=True);r['directories'].append(path);continue
            data=get(f,path);assert len(data)==meta['bytes'],path
            local.parent.mkdir(parents=True,exist_ok=True);assert not local.exists();local.write_bytes(data)
            assert sha(local.read_bytes())==sha(data)
            r['files'][path]=dict(bytes=len(data),sha256=sha(data))
            if len(r['files'])%500==0:save();print('Captured',len(r['files']),'Windows files',flush=True)
        # All critical live hives and drivers must still match the start of capture.
        critical=['/F/winnt/system32/config/'+n for n in ['system','software','sam','security','default']]
        critical += ['/F/winnt/system32/drivers/'+n for n in ['xwnfatx.sys','xboxvnt5.sys','xwnaci207.sys']]
        critical += ['/F/winnt/system32/xwnown.dll']
        for path in critical:
            actual=next(n for n in r['files'] if n.lower()==path.lower());assert sha(get(f,actual))==r['files'][actual]['sha256']
        boot='/E/Applications/XWNFBoot';queue=[boot]
        for folder in queue:
            for name,meta in names(f,folder).items():
                path=folder+'/'+name
                if meta['directory']:queue.append(path);continue
                data=get(f,path);local=P/path.lstrip('/');local.parent.mkdir(parents=True,exist_ok=True);assert not local.exists();local.write_bytes(data)
                r['files'][path]=dict(bytes=len(data),sha256=sha(data))
        r.update(complete=True,finished_utc=utc(),logical_bytes=sum(v['bytes'] for v in r['files'].values()),file_count=len(r['files']))
except BaseException as e:r['error']=repr(e);raise
finally:save()
print('Read-only Windows/boot capture complete',r['file_count'],r['logical_bytes'],flush=True)
