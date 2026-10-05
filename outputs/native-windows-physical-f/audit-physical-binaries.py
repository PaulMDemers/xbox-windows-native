"""Read-only FTP audit of owned Windows binaries and registry snapshots.

This does not inspect FAT allocation chains or prove RAM/driver correctness.
"""
import argparse,datetime,ftplib,hashlib,io,json,os,pathlib
p=argparse.ArgumentParser();p.add_argument('--cycle',type=int,default=11);p.add_argument('--resume',action='store_true');a=p.parse_args()
assert 1 <= a.cycle <= 999
tag=f'{a.cycle:03d}'
k=pathlib.Path(__file__).resolve().parent
r={'scope':__doc__,'cycle':a.cycle,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checked':0,'bytes':0,'mismatches':[],'hives':[],'complete':False}
out=k/f'physical-{tag}-binary-audit.json';assert a.resume or not out.exists()
cycle=json.loads((k/f'physical-cycle-{tag}.json').read_text())
manifest=json.loads((k/'package-manifest.json').read_text())['files']
ext={'.exe','.dll','.sys','.nls','.fon','.ttf','.cpl','.ocx'}
items=[v for v in manifest if v['path'].startswith('F/') and pathlib.PurePosixPath(v['path']).suffix.lower() in ext]
overrides={'F/winnt/system32/drivers/xwnfatx.sys':cycle['filesystem_sha256'],'F/winnt/system32/drivers/xboxvnt5.sys':cycle['miniport_sha256']}
r['expected_count']=len(items);r['overrides']=overrides
start=0
if a.resume:
    prior=json.loads(out.read_text());assert not prior['complete'] and not prior['hives']
    assert prior['cycle']==a.cycle and prior['expected_count']==len(items) and prior['overrides']==overrides
    backup=out.with_name(out.stem+f"-interrupted-{prior['checked']}.json");assert not backup.exists();backup.write_bytes(out.read_bytes())
    r=prior;start=r['checked'];r.pop('error',None);r['resumed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():out.write_text(json.dumps(r,indent=2)+'\n')
def get(f,name):
    b=io.BytesIO();f.retrbinary('RETR '+name,b.write);return b.getvalue()
try:
 with ftplib.FTP() as f:
    f.connect(cycle['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    f.cwd('/F');assert json.loads(get(f,'xwn-deploy-v1.json'))==json.loads((k/'physical-cache-preflight.json').read_text())['ownership_marker']
    for name,wanted in overrides.items():assert hashlib.sha256(get(f,'/'+name)).hexdigest()==wanted
    directory=None
    for v in items[start:]:
        if r['checked'] and r['checked']%250==0:
            f.quit();f.connect(cycle['host'],timeout=15);f.login('xbox',os.environ['XWN_FTP_PASSWORD']);directory=None
        path=pathlib.PurePosixPath('/'+v['path'])
        if str(path.parent)!=directory:f.cwd(str(path.parent));directory=str(path.parent)
        h=hashlib.sha256();size=[0]
        def consume(b):h.update(b);size[0]+=len(b)
        f.retrbinary('RETR '+path.name,consume,blocksize=65536)
        expected=overrides.get(v['path'],v['sha256'])
        if h.hexdigest()!=expected:r['mismatches'].append({'path':v['path'],'expected':expected,'actual':h.hexdigest(),'bytes':size[0]})
        r['checked']+=1;r['bytes']+=size[0]
        if r['checked']%250==0:save();print(r['checked'],'checked;',len(r['mismatches']),'mismatches',flush=True)
    f.cwd('/F/winnt/system32/config')
    for name in ['system','software','sam','security','default']:
        b=get(f,name);p=k/'artifacts'/('physical-'+tag+'-'+name)
        if p.exists():assert p.read_bytes()==b
        else:p.write_bytes(b)
        r['hives'].append({'name':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 r['complete']=True;r['passed']=not r['mismatches']
except Exception as e:r['error']=repr(e);raise
finally:r['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(r,indent=2))
