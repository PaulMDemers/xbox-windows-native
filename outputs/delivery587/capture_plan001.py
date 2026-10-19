"""Inventory only the Windows E installation and normal launcher; no console writes."""
from pathlib import Path
import importlib.util,json,shutil,time
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('probe587',K/'console_probe001.py')
# Import the transport directly: the one-shot probe itself must not rerun.
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
p=importlib.util.module_from_spec(s);s.loader.exec_module(p);m=p.m
P=Path('E:/xwn587/windows-capture001');assert not P.exists();P.mkdir(parents=True)
out=K/'capture-plan001.json';assert not out.exists()
roots=['/E/winnt','/E/documents and settings','/E/program files','/E/Applications/XWNEBoot']
manifest={'files':{},'directories':[]};r={'complete':False,'console_writes':False,'console_c_accessed':False,'private_root':str(P)}
start=time.monotonic()
try:
    with m.connect(timeout=20) as ftp:
        m.baseline(ftp,'720p')
        assert {n.lower() for n in m.names(ftp,m.START)}<={'xwnsetup.cmd','desktop.ini'}
        for name in (m.NORMAL,m.TARGET,'/E/Applications/XWNEBoot/freeldr.ini'):
            data=m.get(ftp,name);dest=P/'review'/name.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        todo=list(roots)
        while todo:
            assert time.monotonic()-start<600
            d=todo.pop();assert d not in manifest['directories'];manifest['directories'].append(d)
            for name,row in m.names(ftp,d).items():
                assert name not in ('','.','..') and '/' not in name and '\\' not in name
                remote=d+'/'+name
                if row['directory']:todo.append(remote)
                else:manifest['files'][remote]={'bytes':row['bytes']}
            assert len(manifest['files'])<12000 and len(manifest['directories'])<2000
            if len(manifest['directories'])%50==0:print(json.dumps({'dirs':len(manifest['directories']),'files':len(manifest['files'])}),flush=True)
    total=sum(x['bytes'] for x in manifest['files'].values())
    assert total<1536*1024**2 and shutil.disk_usage('E:/').free-total>20*1024**3
    dest=P/'inventory.json';dest.write_text(json.dumps(manifest,indent=2)+'\n')
    r.update(complete=True,files=len(manifest['files']),directories=len(manifest['directories']),bytes=total,manifest_sha256=m.sha(dest.read_bytes()))
except BaseException as e:r['error_type']=type(e).__name__;raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
