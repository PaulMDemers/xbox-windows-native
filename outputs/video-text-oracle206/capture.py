"""Read-only dashboard capture and private rollback; no STOR, startup edit or launch."""
import datetime,hashlib,importlib.util,json,os,zipfile
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'capture.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('ftp_helpers',ws/'outputs/fatx0098-soak3/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
baseline=json.loads((ws/'outputs/fatx0101-physical/installed-state.json').read_text())
art=k/'artifacts';assert art.is_dir()
creation=json.loads((k/'creation.json').read_text())
for name,field in [('runner.exe','runner_sha256'),('replay.exe','probe_sha256')]:
    assert hashlib.sha256((art/name).read_bytes()).hexdigest()==creation[field]
assert not (art/'F').exists() and not (art/'E').exists()
sha=lambda data:hashlib.sha256(data).hexdigest()
r=dict(scope=__doc__,utc=m.utc(),source_sha256=sha(Path(__file__).read_bytes()),physical_access=True,
       physical_writes=False,launch_attempted=False,files=[],passed=False,host=os.environ['XWN_FTP_HOST'])
def save():dest.write_text(json.dumps(r,indent=2)+'\n')
paths=list(baseline['checks'])
paths += ['/F/winnt/system32/config/default','/F/winnt/system32/config/sam','/F/winnt/system32/config/security','/F/winnt/system32/win32k.sys','/E/Applications/XWNFBoot/loader/xboxbvid.dll','/F/winnt/system32/config/system','/F/winnt/system32/config/software',
          '/F/winnt/system32/config/sysevent.evt','/F/winnt/system32/config/appevent.evt','/F/winnt/setupapi.log',m.startup,
          '/F/winnt/system32/xwn-video-trace.bin','/F/winnt/system32/drivers/atapi.sys','/F/winnt/system32/drivers/nvnetnt5.sys',
          '/F/winnt/system32/ntoskrnl.exe','/F/winnt/system32/drivers/videoprt.sys']
providers=json.loads((k.parent/'video-measurement-boundary194/build-review.json').read_text())['providers']
paths += ['/F/winnt/system32/'+name for name in providers]
save()
try:
    with m.connect() as f:
        m.owner(f);r['project_ownership_verified']=True;r['dashboard_reply']=f.getwelcome();save()
        for path in dict.fromkeys(paths):
            data=m.get(f,path);assert len(data)<=8*1024*1024
            p=art/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            expected=providers.get(path.rsplit('/',1)[1],{}).get('sha256',baseline['checks'].get(path,{}).get('sha256'))
            row=dict(path=path,bytes=len(data),sha256=sha(data),expected_last_physical_sha256=expected,
                     matches_last_physical=None if expected is None else sha(data)==expected,second_read_exact=False)
            r['files'].append(row);save()
            assert m.get(f,path)==data,'Changed during read-only capture: '+path
            row['second_read_exact']=True;save()
            if expected:assert row['matches_last_physical'],'Physical baseline changed: '+path
        startup=next(v for v in r['files'] if v['path']==m.startup)
        assert startup['sha256']==baseline['startup_sha256'],'Normal startup differs'
    rollback=['F/winnt/system32/drivers/xboxvnt5.sys','F/winnt/system32/framebuf.dll','E/Applications/XWNFBoot/loader/xboxbvid.dll',
              'F/winnt/system32/config/system','F/winnt/system32/config/software',m.startup.lstrip('/')]
    p=art/'current-display-rollback206.zip'
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in rollback:z.writestr(name,(art/name).read_bytes())
    with zipfile.ZipFile(p) as z:
        assert set(z.namelist())==set(rollback) and all(z.read(n)==(art/n).read_bytes() for n in rollback)
    r.update(passed=True,current_rollback=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p.read_bytes()),entries=len(rollback),readback_verified=True),completed_utc=m.utc())
    save();print('Read-only physical hashes/configuration and current rollback captured; no write/launch')
except Exception as exc:r.update(error=repr(exc),failed_utc=m.utc());save();raise
