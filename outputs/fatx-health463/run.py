"""Fresh read-only E allocation capture using unchanged qualified scanner341."""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
P = Path('E:/xwn463/scan001')
REMOTE = '/F/Applications/XWNFatx463a'
BIN = Path('E:/xwn341/build001/bin/default.xbe')
ANALYZER = W / 'outputs/hd-phase-runtime346/analyze-allocation002.py'
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from physical import baseline, connect, get, put, names, sha, utc, write_json, START, NORMAL, TARGET, ticket

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def verify():
    ticket()
    build = read(W/'outputs/stock-scan341/build001.json')
    for name,h in build['source'].items():
        assert sha((W/'outputs/stock-scan341'/name).read_bytes()) == h
    data = BIN.read_bytes()
    assert sha(data) == build['outputs']['default.xbe']['sha256'] == '66e58932a1c3cd647d8ffd7bec825835f4d92a8b337e40fffd7d7acea2249967'
    return data

def preflight():
    data = verify()
    assert not (K/'preflight001.json').exists() and not P.exists()
    space = {d:shutil.disk_usage(d).free for d in ['C:/','E:/']}
    assert all(n-8*1024**2 >= 20*1024**3 for n in space.values())
    pins = [Path(__file__),ANALYZER,W/'outputs/stock-scan341/main.c',W/'outputs/stock-scan341/build001.json',W/'outputs/field-scanout428/physical.py',W/'outputs/demo-audio-level256/common001.py',W/'outputs/surface-bridge260/atomic_json.py',W/'tools/configure-e-display.py',W/'tools/e-display-policy.json']
    write_json(K/'preflight001.json',dict(passed=True,utc=utc(),space=space,read_partition='E',output_partition='F',console_C_accessed=False,repair=False,source_pins={str(p):sha(p.read_bytes()) for p in pins},binary_sha256=sha(data),prior_scan='setup-candidate398/candidate001/after-scan'))
    print('Preflight passed: unchanged scanner, pinned inputs, fresh IDs and capacity')

def pins():
    for p,h in read(K/'preflight001.json')['source_pins'].items():
        assert sha(Path(p).read_bytes()) == h,p

def stage_launch():
    data = verify(); pins()
    out = K/'trial001.json'
    assert not out.exists() and not P.exists()
    P.mkdir(parents=True)
    r = dict(utc=utc(),launch_requested=False,remote=REMOTE,read_partition='E',output_partition='F',console_C_accessed=False,repair=False,before={})
    write_json(out,r)
    prior = read(W/'outputs/boot-refusal462/collection001.json')
    paths = [NORMAL,TARGET]+['/E/winnt/system32/config/'+n for n in ['system','software','sam','security','default','sysevent.evt','appevent.evt']]+['/E/winnt/system32/xwn-video-trace.bin']
    with connect() as f:
        baseline(f,'720p')
        assert {n.lower() for n in names(f,START)} <= {'xwnsetup.cmd','desktop.ini'}
        assert REMOTE.rsplit('/',1)[1].lower() not in {n.lower() for n in names(f,'/F/Applications')}
        for n in paths:
            b=get(f,n); assert b==get(f,n) and sha(b)==prior['files'][n]['sha256'],n
            r['before'][n]=dict(bytes=len(b),sha256=sha(b))
        write_json(out,r)
        f.mkd(REMOTE); put(f,REMOTE+'/default.xbe',data)
        owner=json.dumps(dict(case='fatx-health463/scan001',binary_sha256=sha(data),read_partition='E',output_partition='F'),sort_keys=True).encode()
        put(f,REMOTE+'/owner.json',owner)
        r['owner_sha256']=sha(owner)
        for n in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            assert get(f,REMOTE+'/'+n,True) is None
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC F:\Applications\XWNFatx463a\default.xbe')
        write_json(out,r);f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(r['command'])
        except Exception as e:r['reply_uncertain']=repr(e)
        write_json(out,r)
    print('One scanner launch recorded; never resend',flush=True)

def observe():
    assert read(K/'trial001.json')['launch_requested'] and not (K/'return001.json').exists()
    r=dict(returned=False,samples=[]);deadline=time.monotonic()+300
    while time.monotonic()<deadline:
        row=dict(utc=utc(),dashboard=False)
        try:
            with connect(timeout=3) as f:
                b=get(f,REMOTE+'/snapshot.txt',True)
            row.update(dashboard=True,completed_report=bool(b and b'SNAPSHOT_COMPLETE success=1 ' in b))
        except (OSError,EOFError) as e:row['error']=type(e).__name__
        r['samples'].append(row);r['returned']=row.get('completed_report',False)
        write_json(K/'return001.json',r)
        if r['returned']:break
        time.sleep(3)
    r['closed']=True;write_json(K/'return001.json',r)
    print('Scanner dashboard return:',r['returned'],flush=True)

def collect():
    pins();data=verify();r=read(K/'trial001.json')
    assert r['launch_requested'] and not (K/'collection001.json').exists()
    c=dict(completed=False,utc=utc(),files={},unchanged={},console_C_accessed=False,remote_writes=[])
    write_json(K/'collection001.json',c)
    with connect() as f:
        assert get(f,REMOTE+'/default.xbe')==data
        assert sha(get(f,REMOTE+'/owner.json'))==r['owner_sha256']
        for n in ['snapshot.txt','fat-metadata.bin','directories.bin']:
            b=get(f,REMOTE+'/'+n);assert b==get(f,REMOTE+'/'+n)
            p=P/n;assert not p.exists();p.write_bytes(b)
            c['files'][n]=dict(path=str(p),bytes=len(b),sha256=sha(b));write_json(K/'collection001.json',c)
        baseline(f,'720p')
        for n,v in r['before'].items():
            b=get(f,n);c['unchanged'][n]=dict(bytes=len(b),sha256=sha(b),unchanged=sha(b)==v['sha256'])
            write_json(K/'collection001.json',c)
        assert all(v['unchanged'] for v in c['unchanged'].values())
    assert not (K/'allocation001.json').exists()
    subprocess.run([sys.executable,'-B',str(ANALYZER),'--capture',str(P),'--output',str(K/'allocation001.json')],check=True)
    c.update(completed=True,ended_utc=utc(),allocation_sha256=sha((K/'allocation001.json').read_bytes()))
    write_json(K/'collection001.json',c)
    print('Captured and analyzed; original boot/startup/hives/events/trace unchanged',flush=True)

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ['preflight','stage_launch','observe','collect']
    globals()[sys.argv[1]]()
