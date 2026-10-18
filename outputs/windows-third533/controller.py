"""One finite third Windows request and read-only new collection."""
import importlib.util,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];PRE=K.parent/'windows-pair532'
s=importlib.util.spec_from_file_location('pair532',PRE/'controller.py');pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read
def verify():
    pair.verify();r=read(K/'preflight001.json');assert r['passed']
    for p,h in r['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    z=read(PRE/'final001.json');a=read(PRE/'audit2.json');o=read(PRE/'observer2.json')
    assert z['closed'] and z['physical_launches']==2 and z['second_all_ten_files_unchanged']
    assert a['closed'] and a['hives_clean'] and a['changed_files']==[]
    assert o['at_dashboard'] and not o['manual_reset_reported']
def launch():
    verify();out=K/'launch.json';assert not out.exists();prior=read(PRE/'after2.json')
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==prior['startup_listing']
        for n,row in prior['files'].items():
            b=m.get(f,n);assert m.sha(b)==row['sha256'] and len(b)==row['bytes'],n
        pair.request_once(f,out,dict(ordinal=3,first_two_closed=True,ordinary_launcher_unchanged=True,
            no_trace_reseed=True,remote_file_writes=[],temporary_hook_installed=False,console_C_accessed=False,
            no_fourth_launch_planned=True,before_sha256=m.sha((PRE/'after2.json').read_bytes())))
def collect():
    verify();assert read(K/'launch.json')['requested']
    out=K/'after.json';folder=Path('C:/xwn533/after');assert not out.exists() and not folder.exists()
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    folder.mkdir(parents=True);r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=m.startup(f);r['ordinary_code_exact']=True
    for n in pair.FILES:
        b=m.cold_pair(n,r,out);assert b is not None
        r['files'][n]=m.keep(folder,n,b);m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('launch','collect');globals()[sys.argv[1]]()
