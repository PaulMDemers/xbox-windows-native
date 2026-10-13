"""Bounded read-only E listing and private recovery ZIP footprint, no C access."""
import hashlib,json,sys,time,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'demo-audio-level256'));from common001 import connect,names,utc
out=K/'inventory001.json';assert not out.exists()
private=Path('E:/xwn333/e-inventory001.json');assert not private.exists()
r=dict(utc=utc(),physical_writes=False,console_c_accessed=False,complete=False,entries={})
deadline=time.monotonic()+180
try:
    with connect(timeout=8) as f:
        queue=['/E'];seen=set()
        for path in queue:
            assert len(queue)<=4096 and time.monotonic()<deadline
            assert path.startswith('/E/') or path=='/E'
            assert path.lower() not in seen;seen.add(path.lower())
            listing=names(f,path)
            for n,v in listing.items():
                assert '/' not in n and '\\' not in n and ':' not in n and n not in ['.','..']
                child=path+'/'+n;r['entries'][child]=v
                if v['directory']:queue.append(child)
    r['complete']=True
finally:
    private.write_text(json.dumps(r,indent=2)+'\n')
summary=dict(physical_writes=False,console_c_accessed=False,listing_complete=r['complete'],
             directories=sum(v['directory'] for v in r['entries'].values())+1,
             files=sum(not v['directory'] for v in r['entries'].values()),
             logical_file_bytes=sum(v['bytes'] for v in r['entries'].values() if not v['directory']),
             private_listing_sha256=hashlib.sha256(private.read_bytes()).hexdigest(),private_listing=str(private))
pin=json.loads((K.parent/'demo-audio-level256/capture-summary.json').read_text())
archives=[]
for archive in pin['bundles']:
    p=Path(archive['path']);assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==archive['sha256']
    with zipfile.ZipFile(p) as z:
        entries=[v for v in z.infolist() if not v.is_dir()]
        archives.append(dict(path=str(p),sha256=archive['sha256'],files=len(entries),
          logical_bytes=sum(v.file_size for v in entries),
          file_clusters_at_16KiB=sum(max(1,(v.file_size+16383)//16384) for v in entries)))
summary['recovery_archives']=archives
summary['limits']='File lengths/cluster-rounded budget only; not a free-cluster query or complete allocation audit. Includes historical recovery files; pagefile, directories and reserve are additional.'
out.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
