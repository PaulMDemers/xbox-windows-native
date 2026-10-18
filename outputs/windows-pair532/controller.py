"""Two planned ordinary Windows launches; host journals only, no console writes."""
import importlib.util,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn532')
sys.dont_write_bytecode=True
sys.path.insert(0,str(K.parent/'visible-dispatch528'))
s=importlib.util.spec_from_file_location('physical528',K.parent/'visible-dispatch528/physical.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
FILES=[m.NORMAL,m.TARGET]+m.MUTABLE
COMMAND=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'

def verify():
    m.ticket();r=read(K/'preflight001.json');assert r['passed']
    for p,h in r['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    assert read(K/'host001.json')['passed']
    assert read(K/'host001.json')['controller_sha256']==m.sha(Path(__file__).read_bytes())

def admit(ordinal,ready,previous=None,observer=None,audit=None):
    assert ordinal in (1,2) and ready['ready'] and ready['cold_power_cycle_reported']
    if ordinal==2:
        assert previous['completed'] and observer['at_dashboard'] and observer['user_report_received']
        assert observer['manual_reset'] is False,'Reset breaks planned consecutive pair'
        assert audit['closed'] and audit['hives_clean'] and audit['ordinary_code_exact']

def snapshot(label):
    verify();assert label in ('before','after1','after2')
    out=K/(label+'.json');folder=P/label;assert not out.exists() and not folder.exists()
    if label!='before':assert read(K/('launch'+label[-1]+'.json'))['requested']
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    folder.mkdir(parents=True)
    r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=m.startup(f);r['ordinary_code_exact']=True
    for n in FILES:
        data=m.cold_pair(n,r,out);assert data is not None,n
        r['files'][n]=m.keep(folder,n,data);m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)

def request_once(f,out,r):
    r.update(utc=m.utc(),requested=True,command=COMMAND,automatic_retry_allowed=False)
    with out.open('x',encoding='utf-8') as stream:json.dump(r,stream,indent=2)
    f.sock.settimeout(20)
    try:r['reply']=f.sendcmd(COMMAND)
    except Exception as e:r['reply_uncertain']=type(e).__name__
    m.write_json(out,r)

def launch(ordinal):
    verify();out=K/f'launch{ordinal}.json';assert not out.exists()
    ready=read(K/'readiness001.json')
    prev=read(K/('before.json' if ordinal==1 else 'after1.json'))
    obs=None if ordinal==1 else read(K/'observer1.json')
    audit=None if ordinal==1 else read(K/'audit1.json')
    admit(ordinal,ready,prev,obs,audit);assert prev['completed']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==prev['startup_listing']
        for n,row in prev['files'].items():
            b=m.get(f,n);assert len(b)==row['bytes'] and m.sha(b)==row['sha256'],n
        r=dict(ordinal=ordinal,before_sha256=m.sha((K/('before.json' if ordinal==1 else 'after1.json')).read_bytes()),
               original_launcher=True,remote_writes=[],temporary_hook_installed=False,console_C_accessed=False,
               no_trace_reset=True,manual_normal_restart_requested=True,automatic_restart_installed=False)
        request_once(f,out,r)

if __name__=='__main__':
    assert len(sys.argv)==2
    action=sys.argv[1]
    if action in ('before','after1','after2'):snapshot(action)
    elif action in ('launch1','launch2'):launch(int(action[-1]))
    else:raise ValueError('Unknown action')
