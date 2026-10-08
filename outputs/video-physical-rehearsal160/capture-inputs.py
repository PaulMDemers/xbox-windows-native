"""Additional read-only physical runtime dependencies for an isolated emulator rehearsal."""
import hashlib,importlib.util,json,os
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'inputs.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('ftp_helpers',ws/'outputs/fatx0098-soak3/physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=ws/'outputs/video-physical-review159';capture=json.loads((base/'capture.json').read_text());assert capture['passed']
art=k/'artifacts';art.mkdir(exist_ok=False);r=dict(scope=__doc__,physical_access=True,physical_writes=False,launch_attempted=False,files=[],passed=False)
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    with m.connect() as f:
        m.owner(f)
        for name in ['system','software']:
            path='/F/winnt/system32/config/'+name;expected=next(v['sha256'] for v in capture['files'] if v['path']==path)
            assert m.sha(m.get(f,path))==expected,'Physical hive changed since159 capture'
        paths=['/F/winnt/system32/'+n for n in ['kernel32.dll','ntdll.dll','gdi32.dll','win32k.sys','user32.dll','setupapi.dll','hidserv.exe']]
        paths+=['/F/winnt/system32/drivers/'+n for n in ['scsiport.sys','disk.sys','classpnp.sys','ftdisk.sys','diskdump.sys','ndis.sys','tcpip.sys']]
        paths+=['/F/winnt/inf/oem2.inf','/F/xwninf102/xwnvideo.inf']
        for path in paths:
            data=m.get(f,path,optional=path.endswith('hidserv.exe'))
            row=dict(path=path,present=data is not None,bytes=0 if data is None else len(data),sha256=None if data is None else m.sha(data))
            if data is not None:
                assert len(data)<=8*1024*1024 and m.get(f,path)==data
                p=art/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            r['files'].append(row);save()
    r.update(passed=True,utc=m.utc(),base_capture_sha256=m.sha((base/'capture.json').read_bytes()));save();print('Physical runtime dependencies captured; no write/launch')
except Exception as exc:r['error']=repr(exc);save();raise
