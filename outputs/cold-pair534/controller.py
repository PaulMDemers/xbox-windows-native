"""Two predeclared power-cycle Windows launches, no remote file writes."""
import importlib.util,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn534')
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read;FILES=pair.FILES
def verify():
    pair.verify();r=read(K/'preflight001.json');assert r['passed']
    for p,h in r['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    assert read(K/'host001.json')['passed'] and read(K/'host001.json')['controller_sha256']==m.sha(Path(__file__).read_bytes())
def admit(ordinal,ready,audit=None):
    assert ordinal in (1,2) and ready['ordinal']==ordinal
    assert ready['ready'] and ready['power_off_on_reported'] and ready['off_wait_requested_seconds']==10
    if ordinal==2:assert audit['closed'] and audit['hives_clean'] and audit['ordinary_code_exact']
def trace_valid(data):return len(data)==4096 and data[:16]==b'XWN-VID-TRACE01\n'
def snapshot(label):
    verify();assert label in ('before1','after1','before2','after2')
    ordinal=int(label[-1]);out=K/(label+'.json');folder=P/label
    assert not out.exists() and not folder.exists()
    if label.startswith('before'):
        admit(ordinal,read(K/f'ready{ordinal}.json'),None if ordinal==1 else read(K/'audit1.json'))
    else:assert read(K/f'launch{ordinal}.json')['requested']
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    folder.mkdir(parents=True);r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=m.startup(f);r['ordinary_code_exact']=True
    for n in FILES:
        b=m.cold_pair(n,r,out);assert b is not None
        r['files'][n]=m.keep(folder,n,b);m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)
def launch(ordinal):
    verify();out=K/f'launch{ordinal}.json';assert not out.exists()
    ready=read(K/f'ready{ordinal}.json');admit(ordinal,ready,None if ordinal==1 else read(K/'audit1.json'))
    before=read(K/f'before{ordinal}.json');assert before['completed']
    prior=read(K.parent/'windows-third533/after.json' if ordinal==1 else K/'after1.json')
    assert prior['completed']
    for n,row in before['files'].items():assert row['sha256']==prior['files'][n]['sha256'],n
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==before['startup_listing']
        for n,row in before['files'].items():
            b=m.get(f,n);assert len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
            if n.endswith('/xwn-video-trace.bin'):assert trace_valid(b)
        pair.request_once(f,out,dict(ordinal=ordinal,condition='power off about10seconds then on, user reported',
            readiness_sha256=m.sha((K/f'ready{ordinal}.json').read_bytes()),before_sha256=m.sha((K/f'before{ordinal}.json').read_bytes()),
            selected_files_unchanged_by_power_cycle=True,original_launcher=True,no_trace_reseed=True,
            remote_file_writes=[],temporary_hook_installed=False,console_C_accessed=False,no_third_launch_planned=True))
if __name__=='__main__':
    assert len(sys.argv)==2;action=sys.argv[1]
    if action in ('before1','after1','before2','after2'):snapshot(action)
    elif action in ('launch1','launch2'):launch(int(action[-1]))
    else:raise ValueError('unknown action')
