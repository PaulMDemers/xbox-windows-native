"""Preserve owned post-failure guest memory for offline ownership review."""
import datetime,hashlib,json,socket
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001';read=lambda p:json.loads(p.read_text())
run=read(case/'run.json');trace=read(case/'trace.json')
assert not run['closed'] and trace['status']=='both_class_failures_captured' and trace['breakpoints_remaining']==0
dest=case/'memory-capture001.json';dump=case/'artifacts/runtime/memory001.bin'
assert not dest.exists() and not dump.exists()
r=dict(scope=__doc__,run_pid=run['pid'],physical_access=False,ordinary_qualified=False,commands=[],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
def command(cmd):
    with socket.create_connection(('127.0.0.1',4854),timeout=60) as s:
        def reply():
            b=b''
            while not b.endswith(b'(qemu) '):
                p=s.recv(65536)
                if not p:raise EOFError('owned monitor closed')
                b+=p
            return b.decode(errors='replace')
        reply();s.sendall((cmd+'\n').encode());result=reply().split('\r\n',1)[-1]
        r['commands'].append(dict(command=cmd,reply=result));return result
try:
    r['started_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();command('stop');command('info registers')
    command('pmemsave 0 0x4000000 "'+dump.as_posix()+'"')
    assert dump.stat().st_size==64*1024*1024
    r['dump_sha256']=hashlib.sha256(dump.read_bytes()).hexdigest();r['dump_size']=dump.stat().st_size
except Exception as e:r['error']=repr(e)
finally:
    command('cont');r['guest_resumed']=True;r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({key:r.get(key) for key in ('error','dump_size','dump_sha256','guest_resumed')}))
