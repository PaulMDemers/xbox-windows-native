"""One new E-only observation. Never retry a sent launch or overwrite a capture."""
import json,shutil,sys
from pathlib import Path
from decode import decode,terminal,paired
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn435')
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline,connect,get,put,names,sha,utc,write_json,NORMAL,TARGET
REMOTE='/E/Applications/XWNPBCompare435B'
def preflight():
    r=json.loads((K/'review004.json').read_text());assert r['passed']
    for p,h in r['files'].items():assert sha(Path(p).read_bytes())==h,p
    assert shutil.disk_usage('C:/').free-16*1024**2>=20*1024**3
    return r
def stage():
    r=preflight();out=K/'physical002-stage.json';assert not out.exists()
    exe=(P/'build001/bin/default.xbe').read_bytes();assert sha(exe)==r['xbe_sha256']
    rec=dict(utc=utc(),completed=False,console_C_accessed=False,windows_changes=False)
    write_json(out,rec)
    with connect() as f:
        baseline(f,'720p')
        assert REMOTE.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/E/Applications')}
        assert get(f,'/E/documents and settings/all users/start menu/programs/startup/xwn428.cmd',True) is None
        rec['normal_startup_sha256']=sha(get(f,NORMAL));rec['launcher_sha256']=sha(get(f,TARGET))
        f.mkd(REMOTE);put(f,REMOTE+'/default.xbe',exe)
        assert get(f,REMOTE+'/default.xbe')==exe
        rec.update(completed=True,xbe_sha256=sha(exe));write_json(out,rec)
def launch():
    preflight();out=K/'physical002-launch.json';assert not out.exists()
    r=json.loads((K/'physical002-stage.json').read_text());assert r['completed']
    with connect() as f:
        baseline(f,'720p');assert sha(get(f,REMOTE+'/default.xbe'))==r['xbe_sha256']
        assert set(names(f,REMOTE))=={'default.xbe'}
        rec=dict(utc=utc(),requested=True,command=r'SITE EXEC E:\Applications\XWNPBCompare435B\default.xbe')
        write_json(out,rec);f.sock.settimeout(20)
        try:rec['reply']=f.sendcmd(rec['command'])
        except Exception as exc:rec['uncertain_reply']=type(exc).__name__
        write_json(out,rec);print(rec)
def collect():
    out=K/'physical002-collection.json';assert not out.exists()
    private=P/'physical002';assert not private.exists();private.mkdir()
    rec=dict(utc=utc(),completed=False,files={},console_C_accessed=False)
    write_json(out,rec)
    try:
        s=json.loads((K/'physical002-stage.json').read_text())
        with connect() as f:
            baseline(f,'720p');assert sha(get(f,NORMAL))==s['normal_startup_sha256']
            assert sha(get(f,TARGET))==s['launcher_sha256']
            for n in sorted(names(f,REMOTE)):
                assert n in {'default.xbe','result.dat','phase-0.dat','phase-1.dat','phase-2.dat','phase-3.dat'},n
                data=get(f,REMOTE+'/'+n);assert data==get(f,REMOTE+'/'+n)
                (private/n).write_bytes(data);rec['files'][n]=dict(bytes=len(data),sha256=sha(data));write_json(out,rec)
        terminal((private/'result.dat').read_bytes())
        rec['modes']=[decode((private/f'phase-{i}.dat').read_bytes(),i) for i in range(4)]
        rec['register_changes']=paired(rec['modes'])
        rec.update(completed=True,scope='Same CPU framebuffer before/after normal PBKit init, not emitted field proof',
                   field_parity_proved=False,signal_qualified=False,normal_windows_shutdown=False,
                   full_disk_audit=False,baseline_unchanged=True,closed_utc=utc())
    except Exception as exc:rec['failure']=repr(exc);raise
    finally:write_json(out,rec)
    print([{k:m[k] for k in ('phase','pixels','physical','allocation')} for m in rec['modes']])
if __name__=='__main__':
    action=sys.argv[1];assert action in ('stage','launch','collect');globals()[action]()
