"""Bounded read-only stack observation of the loaded probe, not a GPU test."""
import json, sys, struct, time, hashlib, datetime, re
from pathlib import Path
from reader004 import Reader
k=Path(__file__).resolve().parent; ws=k.parents[1]
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/instance218-runs/stock-instance218-stack004')
dest=k/'stack004.json'; assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in json.loads((k/'emulator-frozen004.json').read_text()).items(): assert sha(Path(path))==digest,path
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'))
from monitor_capture import command, acquire_monitor_lock
r=dict(passed=False,debugger=True,ordinary_qualified=False,physical_access=False,
       gpu_writes=False,allocator_invoked=False,breakpoints=0,
       source_sha256=sha(Path(__file__)),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
g=None; lock=None; stopped=False
try:
    time.sleep(25);lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True
    g=Reader();r['features']=g.ask('qSupported');r['stop_reply']=g.ask('?');assert r['stop_reply'].startswith(('T','S'))
    raw=command(4594,'info registers');r['registers']=raw
    reg={n:int(re.search(n+r'=([0-9a-fA-F]+)',raw).group(1),16) for n in ['EIP','ESP','EBP','EAX','ECX','EDX']}
    r['register_values']=reg
    def take(a,n):return dict(address=a,bytes=g.read(a,n).hex())
    r['current_code']=take(reg['EIP']-32,96)
    r['stack']=take(reg['ESP'],1024)
    frames=[];fp=reg['EBP'];seen=set()
    for unused in range(12):
        if fp in seen or fp%4 or not 0xd0000000<=fp<=0xdfffffc0:break
        seen.add(fp);b=g.read(fp,64);nxt,ret=struct.unpack_from('<II',b)
        f=dict(frame=fp,next=nxt,return_address=ret,bytes=b.hex())
        if (0x11020<=ret<0x200000) or (0x80010020<=ret<0x800ab500):
            f['return_code']=take(ret-32,64)
        frames.append(f)
        if nxt<=fp or nxt-fp>65536:break
        fp=nxt
    r['frame_chain']=frames
    for name in ['EAX','ECX','EDX']:
        a=reg[name]
        if (0x80000000<=a<0x83ffff80) or (0xd0000000<=a<0xdfffff80):r[name+'_ram']=take(a,128)
    r['app_main']=take(0x11000,64)
    r['passed']=True
except Exception as exc:r['error']=repr(exc);raise
finally:
    if g:g.s.close()
    if stopped:
        try:command(4594,'cont');r['resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
    if lock:lock.close()
    r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    dest.write_text(json.dumps(r,indent=2)+'\n')
    (run/'capture-complete.signal').write_text('stack observation closed\n')
print(json.dumps({n:r.get(n) for n in ['passed','register_values','frame_chain','resumed']}))
