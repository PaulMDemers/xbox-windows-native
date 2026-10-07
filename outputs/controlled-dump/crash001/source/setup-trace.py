"""Reuse reviewed read-only debugger primitives in a new bounded crash observer."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=(k.parent/'dump-map-trace/trace.py').read_text()
helpers=old[old.index('def u32('):old.index('def arm(')]
prefix='''"""Observe one intentional guest crash and dump return; never inject execution."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001';run=ws/'work/runs/nt5-controlled-dump-crash001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
mods=read(k/'modules.json');pes={}
for n,m in mods.items():assert sha(Path(m['path']))==m['sha256'];pes[n]=pefile.PE(m['path'])
review=read(k.parent/'dump-map-trace/sites.json');K=review['kernel_base_expected'];kr=read(k/'kernel-review.json');L=read(k/'layouts.json')['structures']
assert kr['kernel_sha256']==mods['ntoskrnl.exe']['sha256']
owner=read(k.parent/'shutdown-popup-workload/site-review.json')['thread_owner_offset'];utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,intentional_crash=True,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__)),events=[],runtime_pins=[],module_list=[],dependencies={str(p.relative_to(ws)):sha(p) for p in [k.parent/'dump-map-trace/sites.json',k.parent/'native-windows-nt5-kernel/trace-entry.py',k.parent/'native-windows-prebuild/monitor_capture.py',k.parent/'shutdown-popup-workload/site-review.json']})
g=None;stopped=False;armed=set();loaded=[];entry=None;ret=None;lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
'''
body='''
def arm(a):
    if a not in armed:g.bp(a);armed.add(a)
def remove(a):
    if a in armed:g.bp(a,False);armed.remove(a)
def dump_context():
    p=u32(K+kr['sites']['_IopDumpControlBlock']);assert 0x80000000<=p<0xffffff00
    raw=g.read(p,0x60);s=struct.unpack_from('<I',raw,8)[0]
    return dict(pointer=hex(p),raw=raw.hex(),stack_pointer=hex(s),stack_raw=g.read(s,0x90).hex())
def callback_pin(a):
    if not any(v['base']<=a<v['base']+v['size'] for v in loaded):
        for step in range(128):
            base=(a&~4095)-step*4096
            if g.read(base,2)!=b'MZ':continue
            peoff=u32(base+60)
            if not 0x40<=peoff<4096 or g.read(base+peoff,4)!=b'PE\\0\\0':continue
            ts=u32(base+peoff+8);size=u32(base+peoff+0x50)
            matches=[n for n,m in mods.items() if m['timestamp']==ts and m['image_size']==size]
            if len(matches)!=1:continue
            loaded.append(dict(base=base,size=(size+4095)&~4095,name=matches[0],discovery='bounded callback PE scan'))
            r['module_list']=loaded;break
        else:raise AssertionError('Cannot pin actual dump callback within bounded128 pages')
    return pin(a)
bc=K+kr['sites']['_KeBugCheckEx@20'];dump=K+kr['sites']['_IoWriteCrashDump@24'];initret=K+0x21ed4
try:
    command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for a in [bc,dump,initret]:arm(a)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+600
    for hit in range(16):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                if time.monotonic()>=deadline:
                    g.s.settimeout(5);reply=g.interrupt();r['status']='dump_capture_timeout';break
        stopped=True;g.s.settimeout(5)
        if r['status']=='dump_capture_timeout':break
        regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
        a=regs['EIP'];assert a in armed
        if not loaded:loaded=modules();r['module_list']=loaded
        row=dict(index=len(r['events']),utc=utc(),registers={n:hex(v) for n,v in regs.items()},resident_pin=pin(a),**who());r['events'].append(row)
        if a==bc:
            row['kind']='bugcheck_entry';row['arguments']=[hex(v) for v in struct.unpack('<5I',g.read(regs['ESP']+4,20))]
            row['caller']=hex(u32(regs['ESP']));row['caller_pin']=pin(u32(regs['ESP']))
            assert row['arguments']==['0xe058d103','0x44554d50','0x103','0x10000','0x1'],'Unexpected bugcheck'
            row['storage_pins']={n:pin(next(v['base'] for v in loaded if v['name'].lower()==n)+pes[n].OPTIONAL_HEADER.AddressOfEntryPoint) for n in ['hal.dll','xwnfatx.sys','atapi.sys','disk.sys','classpnp.sys','ftdisk.sys']}
            row['dump_context']=dump_context();remove(bc)
        elif a==dump:
            row['kind']='dump_entry';assert entry is None and r['events'][0]['kind']=='bugcheck_entry'
            row['arguments']=[hex(v) for v in struct.unpack('<6I',g.read(regs['ESP']+4,24))]
            assert row['arguments'][:5]==r['events'][0]['arguments']
            entry=dict(stack=regs['ESP'],thread=row['thread'],return_address=u32(regs['ESP']));ret=entry['return_address'];row['pair']=entry;row['context']=dump_context();arm(ret)
        elif a==initret:
            row['kind']='dump_stack_initialized';assert entry is not None
            row['status']=hex(regs['EAX']);row['context']=dump_context()
            if regs['EAX']<0x80000000:
                raw=bytes.fromhex(row['context']['stack_raw']);callbacks=[struct.unpack_from('<I',raw,v)[0] for v in [0x30,0x34]]
                row['callbacks']=[dict(address=hex(v),pin=callback_pin(v)) for v in callbacks]
        elif a==ret:
            row['kind']='dump_return';assert row['thread']==entry['thread'] and regs['ESP']==entry['stack']+28
            row['eax']=hex(regs['EAX']);row['returned_boolean']=regs['EAX']&255;row['final_status']=hex(u32(K+kr['sites']['_IopFinalCrashDumpStatus']));row['context']=dump_context()
            r['status']='dump_return_observed';save();break
        save()
    else:r['status']='hit_limit'
except BaseException as exc:
    r.update(status='capture_incomplete',error=repr(exc));save()
finally:
    if g:
        if not stopped:
            try:g.s.settimeout(5);g.interrupt();stopped=True
            except Exception as exc:r['interrupt_error']=repr(exc)
        if stopped:
            for a in list(armed):
                try:remove(a)
                except Exception as exc:r.setdefault('breakpoint_cleanup_errors',[]).append([hex(a),repr(exc)])
            try:g.send('c');stopped=False;r['guest_resumed']=True
            except Exception as exc:r['resume_error']=repr(exc)
        g.s.close()
    r['armed_breakpoints_remaining']=[hex(v) for v in sorted(armed)];r['ended_utc']=utc();save();lock.close()
    (out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed'] if n in r},indent=2))
'''
p=k/'trace.py';assert not p.exists();p.write_text(prefix+helpers+body)
