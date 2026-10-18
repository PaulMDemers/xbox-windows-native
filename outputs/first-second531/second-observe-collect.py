"""Bounded read-only second ordinal observation and collection; never launch."""
import importlib.util,json,sys,time,ftplib,shutil
from pathlib import Path
K=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('second531',K/'second-launch.py')
second=importlib.util.module_from_spec(spec);spec.loader.exec_module(second)
m=second.m
P=Path('C:/xwn531/second-physical001')
read=second.read

def observe():
    assert read(K/'second-launch.json')['requested']
    out=K/'second-observation.json';assert not out.exists()
    r=dict(started_utc=m.utc(),completed=False,observations=[],existing_receipts_cannot_prove_second_execution=True)
    m.write_json(out,r);deadline=time.monotonic()+90
    # Do not infer completion from an immediate FTP response during dispatch.
    time.sleep(35)
    while time.monotonic()<deadline:
        try:
            with m.connect(timeout=3) as f:
                rows=m.listing(f)
                files={n:None if n not in rows else m.sha(m.receipt(f,n,rows)) for n in m.RECEIPTS}
            r['observations'].append(dict(utc=m.utc(),dashboard=True,receipt_hashes=files))
            r.update(completed=True,ended_utc=m.utc());m.write_json(out,r);return
        except (OSError,EOFError) as exc:
            r['observations'].append(dict(utc=m.utc(),dashboard=False,error_type=type(exc).__name__))
        except (AssertionError,ValueError,ftplib.Error) as exc:
            r.update(ended_utc=m.utc(),error_type=type(exc).__name__);m.write_json(out,r);raise
        m.write_json(out,r);time.sleep(5)
    r.update(completed=True,deadline_reached=True,ended_utc=m.utc());m.write_json(out,r)

def collect():
    assert read(K/'second-launch.json')['requested'];m.verify()
    out=K/'second-collection.json';assert not out.exists() and not P.exists()
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    prior=read(second.FIRST/'physical001-collection.json')
    stage=read(second.FIRST/'physical001-stage.json')
    P.mkdir(parents=True)
    r=dict(completed=False,started_utc=m.utc(),files={},remote_writes=[],temporary_hook_installed=False,
           console_C_accessed=False,existing_receipts_cannot_prove_second_execution=True)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=m.startup(f)
        assert r['startup_listing']==stage['startup_listing'];r['protected_code_exact']=True
    for n,old in prior['files'].items():
        b=m.cold_pair(n,r,out)
        if b is None:r['files'][n]=None
        else:
            row=m.keep(P/'after',n,b)
            row['unchanged_from_first']=old is not None and row['sha256']==old['sha256'] and row['bytes']==old['bytes']
            r['files'][n]=row
        m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('observe','collect')
    globals()[sys.argv[1]]()
