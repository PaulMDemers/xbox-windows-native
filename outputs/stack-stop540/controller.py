"""One intentional post-stack halt; no Windows boot or startup hook."""
import importlib.util,json,shutil,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn540/physical001')
s=importlib.util.spec_from_file_location('pair534',K.parent/'cold-pair534/controller.py')
old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
m=old.m;read=old.read;FILES=old.FILES
RECEIPTS=('report.bin','handoff.bin','context.bin','refusal.bin')
def admit(i,ready,audit=None,observer=None):
    assert i==1 and ready['ordinal']==1 and ready['ready']
    assert ready['watching_LED'] and ready['manual_reset_available']


def verify():
    old.verify();q=read(K/'package001.json');assert q['passed']
    for p,h in q['pins'].items():assert m.sha(Path(p).read_bytes())==h,p
    for row in q['images'].values():assert m.sha(Path(row['path']).read_bytes())==row['sha256']
    return q
def owner(i,row):
    return json.dumps(dict(project='xbox-windows-native',case='stack-stop540',ordinal=i,
        diagnostic_schema=490,sha256=row['sha256']),sort_keys=True).encode()
def receipt(f,remote,name,rows):
    assert name in RECEIPTS
    if name not in rows:return None
    row=rows[name];assert not row['directory'] and 0<=row['bytes']<=4096
    chunks=[];total=0
    def take(b):
        nonlocal total
        total+=len(b)
        if total>4096:raise ValueError('oversize receipt')
        chunks.append(b)
    f.retrbinary('RETR '+remote+'/'+name,take,1024)
    data=b''.join(chunks);assert len(data)==row['bytes']
    return data
def exact_stage(f,i,row):
    remote=row['remote'];assert m.get(f,remote+'/owner.json')==owner(i,row)
    assert m.sha(m.get(f,remote+'/default.xbe'))==row['sha256']
def stage():
    q=verify();out=K/'stage001.json';assert not out.exists()
    r=dict(completed=False,utc=m.utc(),writes=[],console_C_accessed=False,temporary_hook_installed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');m.startup(f)
        names={n.lower() for n in m.names(f,'/E/Applications')}
        assert all(row['remote'].rsplit('/',1)[1].lower() not in names for row in q['images'].values())
        for i in (1,):
            row=q['images'][str(i)];remote=row['remote']
            r['writes'].append(remote);m.write_json(out,r);f.mkd(remote)
            for n,b in [('owner.json',owner(i,row)),('default.xbe',Path(row['path']).read_bytes())]:
                target=remote+'/'+n;r['writes'].append(target);m.write_json(out,r)
                m.put(f,target,b);assert m.get(f,target)==b
            exact_stage(f,i,row)
        m.baseline(f,'720p');m.startup(f)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)
def snapshot(label):
    q=verify();assert label in ('before1','after1')
    i=int(label[-1]);out=K/(label+'.json');folder=P/label
    assert not out.exists() and not folder.exists() and read(K/'stage001.json')['completed']
    if label.startswith('before'):
        admit(i,read(K/f'ready{i}.json'),None if i==1 else read(K/'audit1.json'),None if i==1 else read(K/'observer1.json'))
    else:
        assert read(K/f'launch{i}.json')['requested']
        obs=read(K/'observer1.json');assert obs['at_dashboard'] and obs['user_report_received']
    assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3
    folder.mkdir(parents=True)
    r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup_listing']=m.startup(f);r['ordinary_code_exact']=True
        exact_stage(f,i,q['images'][str(i)])
    for n in FILES:
        b=m.cold_pair(n,r,out);assert b is not None
        r['files'][n]=m.keep(folder,n,b);m.write_json(out,r)
    if label.startswith('after'):
        remote=q['images'][str(i)]['remote'];r['receipts']={}
        with m.connect(timeout=15) as f:
            rows=m.names(f,remote)
            assert set(rows)<={'owner.json','default.xbe',*RECEIPTS}
            for name in RECEIPTS:
                a=receipt(f,remote,name,rows);b=receipt(f,remote,name,m.names(f,remote))
                assert a==b,'receipt changed'
                r['receipts'][name]=None if a is None else m.keep(folder,remote+'/'+name,a)
                m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)
def request_once(f,out,r,command):
    r.update(utc=m.utc(),requested=True,command=command,automatic_retry_allowed=False)
    with out.open('x',encoding='utf-8') as stream:json.dump(r,stream,indent=2)
    f.sock.settimeout(20)
    try:r['reply']=f.sendcmd(command)
    except Exception as e:r['reply_uncertain']=type(e).__name__
    m.write_json(out,r)
def launch_command(i):
    assert i==1
    return r'SITE EXEC E:\Applications\XWNBoot540a\default.xbe'


def launch(i):
    q=verify();out=K/f'launch{i}.json';assert not out.exists()
    ready=read(K/f'ready{i}.json')
    admit(i,ready,None if i==1 else read(K/'audit1.json'),None if i==1 else read(K/'observer1.json'))
    before=read(K/f'before{i}.json');assert before['completed']
    prior=read(K.parent/'entry-footprint539/after1.json')
    assert prior['completed']
    for n,row in before['files'].items():assert row['sha256']==prior['files'][n]['sha256'],n
    row=q['images'][str(i)];remote=row['remote']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==before['startup_listing'];exact_stage(f,i,row)
        assert set(m.names(f,remote))=={'owner.json','default.xbe'}
        for n,v in before['files'].items():
            b=m.get(f,n);assert len(b)==v['bytes'] and m.sha(b)==v['sha256'],n
            if n.endswith('/xwn-video-trace.bin'):assert old.trace_valid(b)
        command=launch_command(i)
        request_once(f,out,dict(ordinal=i,readiness_sha256=m.sha((K/f'ready{i}.json').read_bytes()),
            before_sha256=m.sha((K/f'before{i}.json').read_bytes()),image_sha256=row['sha256'],
            no_temporary_hook=True,manual_normal_restart=False,intentional_halt=True,windows_boot_intended=False,manual_reset_required=True,console_C_accessed=False),command)
if __name__=='__main__':
    assert len(sys.argv)==2;action=sys.argv[1]
    if action=='stage':stage()
    elif action in ('before1','after1'):snapshot(action)
    elif action in ('launch1',):launch(int(action[-1]))
    else:raise ValueError('unknown action')
