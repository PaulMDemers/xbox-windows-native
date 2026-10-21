"""Prepared one-shot standalone display trial. No Windows or startup hook."""
import importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn631/physical001')
sys.path.insert(0,str(K))
spec_decode=importlib.util.spec_from_file_location('decode631',K/'decode.py')
decoder=importlib.util.module_from_spec(spec_decode);spec_decode.loader.exec_module(decoder)
decode=decoder.decode
assert Path(sys.modules['oracle'].__file__).resolve()==(K/'oracle.py').resolve()
sys.path.insert(0,str(K.parent/'visible-dispatch528'))
spec=importlib.util.spec_from_file_location('scope631',K.parent/'visible-dispatch528/physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REMOTE='/E/Applications/XWNMode631'
COMMAND=r'SITE EXEC E:\Applications\XWNMode631\default.xbe'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))

def verify():
    m.ticket()
    # This missing record is intentional until actual physical readiness and
    # separate scope review exist. Emulator disk audit is never rewritten.
    admission=read(K/'physical-admission001.json')
    assert admission['original_console_ready'] and admission['watched_transition']
    assert admission['standalone_scope_reviewed'] and admission['reserved_disk_delta_reviewed']
    assert admission['whole_disk_equality_passed'] is False
    for path,h in admission['source_pins'].items():assert m.sha(Path(path).read_bytes())==h,path
    tests=read(K/'physical-host001.json');assert tests['passed']
    assert tests['controller_sha256']==m.sha(Path(__file__).read_bytes())
    proof=read(K/'final-review001.json');assert proof['closed'] and proof['mode_trace_passed']
    assert proof['whole_disk_equality_passed'] is False
    b=Path('C:/xwn631/build001/bin/default.xbe').read_bytes()
    assert m.sha(b)==read(K/'binary-review001.json')['xbe_sha256']
    assert shutil.disk_usage('C:/').free-128*1024**2>=20*1024**3
    return b

def listing(f):
    rows=m.names(f,REMOTE)
    assert set(rows)<={'owner.json','default.xbe','hd631.txt'}
    assert all(not v['directory'] for v in rows.values())
    if 'hd631.txt' in rows:assert rows['hd631.txt']['bytes']<=32768
    return rows

def stage():
    b=verify();out=K/'physical-stage001.json';assert not out.exists() and not P.exists()
    P.mkdir(parents=True)
    r=dict(completed=False,utc=m.utc(),before={},writes=[],console_C_accessed=False,temporary_hook=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');r['startup']=m.startup(f)
        assert REMOTE.rsplit('/',1)[1].lower() not in {n.lower() for n in m.names(f,'/E/Applications')}
        for n in [m.NORMAL,m.TARGET]+m.MUTABLE:
            a=m.get(f,n);assert a==m.get(f,n);r['before'][n]=m.keep(P/'before',n,a);m.write_json(out,r)
        r['writes'].append(REMOTE);m.write_json(out,r);f.mkd(REMOTE)
        owner=json.dumps(dict(project='xbox-windows-native',attempt='631physical001',scope='standalone480p720p480p',xbe_sha256=m.sha(b)),sort_keys=True).encode()
        for name,data in [('owner.json',owner),('default.xbe',b)]:
            n=REMOTE+'/'+name;r['writes'].append(n);m.write_json(out,r);m.put(f,n,data)
            assert m.get(f,n)==data;r.setdefault('staged',{})[n]=dict(bytes=len(data),sha256=m.sha(data));m.write_json(out,r)
        assert set(listing(f))=={'owner.json','default.xbe'}
        m.baseline(f,'720p');assert m.startup(f)==r['startup']
    r.update(completed=True,ended_utc=m.utc());m.write_json(out,r)

def request_once(f,out):
    # Exclusive local creation consumes the attempt before any request, including
    # a failed or uncertain transport. No retry path exists.
    r=dict(requested=True,utc=m.utc(),command=COMMAND,automatic_retry=False,windows_launch=False)
    with out.open('x',encoding='utf-8') as stream:json.dump(r,stream,indent=2)
    f.sock.settimeout(20)
    try:r['reply']=f.sendcmd(COMMAND)
    except Exception as e:r['reply_uncertain']=type(e).__name__
    m.write_json(out,r)

def launch():
    verify();s=read(K/'physical-stage001.json');assert s['completed']
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');assert m.startup(f)==s['startup']
        for n,v in {**s['before'],**s['staged']}.items():assert m.sha(m.get(f,n))==v['sha256'],n
        assert set(listing(f))=={'owner.json','default.xbe'}
        request_once(f,K/'physical-launch001.json')

def collect():
    assert read(K/'physical-launch001.json')['requested']
    out=K/'physical-collection001.json';assert not out.exists()
    s=read(K/'physical-stage001.json');r=dict(completed=False,utc=m.utc(),after={},hook_installed=False,console_C_accessed=False)
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        # No owned hook exists. Refuse any unexpected startup entry first.
        assert m.startup(f)==s['startup'];m.baseline(f,'720p');rows=listing(f)
        assert 'hd631.txt' in rows,'No result; preserve failure, never relaunch'
        data=m.get(f,REMOTE+'/hd631.txt');assert len(data)==rows['hd631.txt']['bytes']<=32768
        assert data==m.get(f,REMOTE+'/hd631.txt')
        target=K/'physical-log001.txt';assert not target.exists();target.write_bytes(data)
        r['log_sha256']=m.sha(data);m.write_json(out,r)
        for n,v in {**s['before'],**s['staged']}.items():
            a=m.get(f,n);assert a==m.get(f,n);r['after'][n]=m.keep(P/'after',n,a);m.write_json(out,r)
            assert r['after'][n]['sha256']==v['sha256'],n
        r['decoded']=decode(data)
    r.update(completed=True,ended_utc=m.utc(),dashboard_returned=True,protected_files_unchanged=True,normal_windows_shutdown_claim=False,visual_output='pending user observation')
    m.write_json(out,r)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ('stage','launch','collect')
    globals()[sys.argv[1]]()
