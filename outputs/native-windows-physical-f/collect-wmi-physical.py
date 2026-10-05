"""Read-only bounded WMI log/repository preservation while dashboard FTP is up."""
import argparse, datetime, ftplib, hashlib, io, json, os, pathlib
p=argparse.ArgumentParser();p.add_argument('--cycle',required=True,type=int);a=p.parse_args()
assert 1<=a.cycle<=999
k=pathlib.Path(__file__).resolve().parent;tag=f'{a.cycle:03d}'
cycle=json.loads((k/f'physical-cycle-{tag}.json').read_text())
out=k/f'physical-{tag}-wmi-files.json';assert not out.exists()
target=k/'artifacts'/f'physical-{tag}-wmi';target.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
r={'scope':__doc__,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[],'total_bytes':0}
def get(f,name,allow_partial=False):
    b=io.BytesIO()
    def consume(chunk):
        assert b.tell()+len(chunk)<=32*1024*1024,'File exceeds collection bound'
        assert r['total_bytes']+b.tell()+len(chunk)<=64*1024*1024,'Total exceeds collection bound'
        b.write(chunk)
    try:f.retrbinary('RETR '+name,consume,blocksize=65536)
    except ftplib.all_errors as e:
        if allow_partial:return b.getvalue(),repr(e)
        raise
    return (b.getvalue(),None) if allow_partial else b.getvalue()
with ftplib.FTP() as f:
    f.connect(cycle['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F');assert json.loads(get(f,'xwn-deploy-v1.json'))==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    for directory in ['logs','repository']:
        f.cwd('/F/winnt/system32/wbem/'+directory)
        names=f.nlst();assert len(names)<=64
        for raw in names:
            name=raw.replace('\\','/').rsplit('/',1)[-1]
            if name in ('.','..'):continue
            assert name not in ('.','..','') and ':' not in name and '\r' not in name and '\n' not in name
            data,error=get(f,name,True);local=target/(directory+'-'+name+('.partial' if error else ''))
            if local.exists():assert local.read_bytes()==data
            else:local.write_bytes(data)
            row={'path':'F/winnt/system32/wbem/'+directory+'/'+name,'bytes':len(data),'sha256':sha(data),'complete':error is None}
            if error:row['error']=error
            original=k/'package'/row['path'].lower().replace('f/','F/',1)
            if original.exists():row['matches_original_package']=original.read_bytes()==data
            r['files'].append(row);r['total_bytes']+=len(data)
r['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
