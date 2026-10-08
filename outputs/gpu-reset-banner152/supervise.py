"""One reset at a native marker, then one post-reset probe; emulator loopback only."""
import datetime,ftplib,hashlib,json,os,socket,sys,time
from pathlib import Path
from ftp_deadline import DeadlineFTP
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control001','candidate001']
sys.path.insert(0,str(ws/'outputs/video-surface-history'));from lifecycle import parse
out=k/case;run=ws/('work/runs/gpu-reset-banner152-'+case);p=out/'reset.json';assert not p.exists()
r=dict(physical_access=False,debugger=False,host='127.0.0.1',port=4596,reset_count=0)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    q=p.with_suffix('.tmp');q.write_text(json.dumps(r,indent=2)+'\n');q.replace(p)
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+8))
    try:
        remaining=f.budget()
        timeout=min(8,remaining)
        started=utc();f.connect('127.0.0.1',4596,timeout=timeout);f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);r.setdefault('ftp_sessions',[]).append(dict(started_utc=started,accepted_utc=utc(),timeout_seconds=timeout));save();return f
    except Exception:f.close();raise
def alive():
    assert not (run/'cleanup.json').exists(),'Runner closed'
    assert (run/'cpu-trace.log').stat().st_size<=16*1024*1024
    assert (run/'nvnet.pcap').stat().st_size<=16*1024*1024
def dashboard(seconds):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        alive()
        try:return connect(deadline)
        except ftplib.all_errors:time.sleep(min(1,max(0,deadline-time.monotonic())))
    raise RuntimeError('No dashboard return; no repeat')
def command(cmd):
    with socket.create_connection(('127.0.0.1',4594),timeout=4) as s:
        s.settimeout(8)
        def prompt():
            b=b''
            while b'(qemu) ' not in b:
                x=s.recv(65536);assert x;b+=x;assert len(b)<1024*1024
            return b.decode('ascii',errors='replace')
        prompt();s.sendall((cmd+'\n').encode());return prompt()
def launch(f,key,path):
    assert key not in r
    r[key]=dict(requested_utc=utc(),command='SITE EXEC '+path,status='requesting',trace_offset=(run/'cpu-trace.log').stat().st_size);save()
    try:r[key].update(reply=f.sendcmd(r[key]['command']),status='accepted')
    except ftplib.all_errors as exc:r[key].update(status='reply_uncertain',error=repr(exc))
    finally:f.close();save()
try:
    f=dashboard(60);launch(f,'before_reset',r'E:\Applications\XWNGpu150\default.xbe')
    deadline=time.monotonic()+120;marker=None
    while time.monotonic()<deadline:
        alive();data=(run/'cpu-trace.log').read_bytes();es=parse(data)
        candidates=[e for e in es if e['offset']>=r['before_reset']['trace_offset'] and e['kind']=='upload' and e.get('binding')=='COLOR' and (e['width'],e['height'],e['pitch'])==(80,40,320)]
        if candidates:marker=candidates[-1];break
        time.sleep(.25)
    assert marker,'No ready marker; no reset'
    r['marker']=marker;r['marker_utc']=utc();save()
    time.sleep(1);alive()
    data=(run/'cpu-trace.log').read_bytes();(out/'before-reset-trace.log').write_bytes(data)
    r.update(before_reset_trace_sha256=hashlib.sha256(data).hexdigest(),reset_trace_offset=len(data),reset_requested_utc=utc(),reset_count=1);save()
    r['reset_pcap_offset']=(run/'nvnet.pcap').stat().st_size;r['pre_reset_network']=command('info network');save()
    r['reset_reply']=command('system_reset');r['reset_command_completed_utc']=utc();save()
    f=dashboard(150);r['reset_dashboard_utc']=utc();r['post_reset_network']=command('info network');r['after_reset_pcap_offset']=(run/'nvnet.pcap').stat().st_size;save()
    launch(f,'after_reset',r'E:\Applications\XWNGpu149\default.xbe')
    deadline=time.monotonic()+150;offline=False
    while time.monotonic()<deadline:
        alive();time.sleep(1)
        try:
            f=connect(deadline);f.close()
            if offline:
                r.update(dashboard_return=True,returned_utc=utc(),offline_after_second_launch=True);save()
                (run/'capture-complete.signal').touch(exist_ok=False);print('One explicit reset and post-reset native run completed',flush=True);break
        except ftplib.all_errors:offline=True
        if time.monotonic()>=deadline:break
    if not r.get('dashboard_return'):raise RuntimeError('Post-reset run did not return')
except Exception as exc:
    r.update(failed=True,error=repr(exc));save()
    try:r['failure_network']=command('info network');save()
    except Exception as capture_error:r['failure_network_error']=repr(capture_error);save()
    (out/'host-stop.json').write_text(json.dumps(dict(success=False,reason=repr(exc),utc=utc()),indent=2)+'\n')
    (run/'capture-complete.signal').touch(exist_ok=False)
    raise
