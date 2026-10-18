"""MIT. One unchanged Windows primer; no remote filesystem mutations."""
import importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn543')
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read

def verify():
    pair.verify()
    r=read(K/'package001.json');assert r['passed']
    for p,h in r['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    assert read(K/'host001.json')['passed']

def admit_after(o):
    assert o['at_dashboard'] and o['user_report_received']
    assert isinstance(o['manual_reset'],bool) and isinstance(o['normal_windows_restart'],bool)
    assert not (o['manual_reset'] and o['normal_windows_restart'])

def snapshot(label):
    verify();assert label in ('before1','after1')
    out=K/(label+'.json');folder=P/label;assert not out.exists() and not folder.exists()
    if label=='after1':
        assert read(K/'launch1.json')['requested'];admit_after(read(K/'observer1.json'))
    else:assert not (K/'launch1.json').exists()
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    folder.mkdir(parents=True)
    r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=m.startup(f);r['ordinary_code_exact']=True
    for n in pair.FILES:
        b=m.cold_pair(n,r,out);assert b is not None,n
        r['files'][n]=m.keep(folder,n,b);m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)

def launch1():
    verify();out=K/'launch1.json';assert not out.exists()
    prev=read(K/'before1.json');assert prev['completed']
    assert read(K.parent/'pre-pci-stop542/final001.json')['closed']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==prev['startup_listing']
        for n,row in prev['files'].items():
            b=m.get(f,n);assert len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
        pair.request_once(f,out,dict(ordinal=1,ordinary_launcher_unchanged=True,
            before_sha256=m.sha((K/'before1.json').read_bytes()),remote_writes=[],
            temporary_hook_installed=False,console_C_accessed=False,no_trace_reseed=True,
            no_automatic_restart=True,one_primer_only=True))

if __name__=='__main__':
    assert len(sys.argv)==2
    if sys.argv[1] in ('before1','after1'):snapshot(sys.argv[1])
    elif sys.argv[1]=='launch1':launch1()
    else:raise ValueError('Unknown action')
