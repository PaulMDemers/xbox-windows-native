"""Bounded fresh read-only Windows snapshot for user's private other-console package."""
from pathlib import Path
import importlib.util,json,shutil,time,hashlib
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
p=importlib.util.module_from_spec(s);s.loader.exec_module(p);m=p.m
plan=json.loads((K/'capture-plan001.json').read_text());assert plan['complete']
source=Path(plan['private_root'])/'inventory.json';assert m.sha(source.read_bytes())==plan['manifest_sha256']
inventory=json.loads(source.read_text());P=Path('C:/xwn587/windows-capture001');assert not P.exists()
assert shutil.disk_usage('C:/').free-plan['bytes']-800*1024**2>20*1024**3
P.mkdir();out=K/'capture001.json';assert not out.exists()
critical=p.FILES+['/E/documents and settings/Win2K/NTUSER.DAT']
r={'complete':False,'root':str(P),'files':0,'bytes':0,'writes_to_console':False,'console_c_accessed':False,'launch_requested':False,'started_utc':m.utc()}
manifest={'files':{},'directories':inventory['directories']};start=time.monotonic()
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    with m.connect(timeout=20) as ftp:
        before={name:m.sha(m.get(ftp,name)) for name in critical}
        assert {n.lower() for n in m.names(ftp,m.START)}<={'xwnsetup.cmd','desktop.ini'}
        for d in inventory['directories']:(P/d.lstrip('/')).mkdir(parents=True,exist_ok=True)
        for name,meta in sorted(inventory['files'].items()):
            assert time.monotonic()-start<1800 and shutil.disk_usage('C:/').free>20.125*1024**3
            dst=P/name.lstrip('/');h=hashlib.sha256();count=0
            with dst.open('xb') as f:
                def receive(data):
                    nonlocal_dummy=None
                    f.write(data);h.update(data)
                ftp.retrbinary('RETR '+name,receive,65536)
            size=dst.stat().st_size;assert size==meta['bytes'],name
            manifest['files'][name]={'bytes':size,'sha256':h.hexdigest()};r['files']+=1;r['bytes']+=size
            if r['files']%100==0:
                save();print(json.dumps({'files':r['files'],'bytes':r['bytes']}),flush=True)
        after={name:m.sha(m.get(ftp,name)) for name in critical};assert before==after
        for name in critical:
            match=next((x for x in manifest['files'] if x.lower()==name.lower()),None)
            assert match and manifest['files'][match]['sha256']==before[name]
        m.baseline(ftp,'720p')
        assert {n.lower() for n in m.names(ftp,m.START)}<={'xwnsetup.cmd','desktop.ini'}
    dest=P/'CAPTURE-MANIFEST.json';dest.write_text(json.dumps(manifest,indent=2)+'\n')
    r.update(complete=True,critical_unchanged=True,manifest_sha256=m.sha(dest.read_bytes()),ended_utc=m.utc())
except BaseException as e:r['error_type']=type(e).__name__;raise
finally:save()
print(json.dumps(r))
