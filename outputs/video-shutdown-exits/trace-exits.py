"""Exploratory owned xemu breakpoint observations; never a qualification run."""
import datetime,json,re,socket,struct,sys,time
from pathlib import Path

k=Path(__file__).resolve().parent;ws=k.parents[1]
src=ws/'outputs/native-windows-nt5-kernel'
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
namespace={}
code=(src/'trace-entry.py').read_text()
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),namespace)
Remote=namespace['Remote']
state=json.loads((k/'runtime.json').read_text());assert state['status'] in ['shell_running','kernel_running']
run=ws/'work/runs/nt5-video-shutdown-exits-001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
pubs=json.loads((src/'kernel-publics.json').read_text())['symbols']
fields=json.loads((src/'process-layouts.json').read_text())['_EPROCESS']['fields']
names=['_NtRaiseHardError@24','_ExRaiseHardError@24','_ExpRaiseHardError@24','_NtTerminateProcess@8']
targets={int(state['kernel_base'],16)+pubs[n]['rva']:n for n in names}
report={'scope':__doc__,'breakpoints':{hex(a):n for a,n in targets.items()},'events':[],'physical_access':False}
lock=acquire_monitor_lock(4594);g=None;armed=set()
def save(): (k/'exit-trace.json').write_text(json.dumps(report,indent=2)+'\n')
def read32(p):return struct.unpack('<I',g.read(p,4))[0]
try:
    command(4594,'stop')
    g=Remote(4595);report['gdb_features']=g.ask('qSupported');report['initial_stop']=g.ask('?')

    for target in targets:g.bp(target);armed.add(target)
    report['verified_entry_bytes']={hex(a):g.read(a,3).hex() for a in targets}
    assert all(v=='558bec' for v in report['verified_entry_bytes'].values())
    save()
    deadline=time.monotonic()+240
    while len(report['events'])<64 and time.monotonic()<deadline:
        g.send('c');g.s.settimeout(max(1,deadline-time.monotonic()))
        response=g.recv();g.s.settimeout(5)
        registers=command(4594,'info registers')
        regs={n:int(v,16) for n,v in re.findall(r'\b(ESP|EIP|CR3)=([0-9a-fA-F]+)',registers)}
        target=regs['EIP'];assert target in targets,(response,regs)
        stack=struct.unpack('<7I',g.read(regs['ESP'],28))
        event={'function':targets[target],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'stop':response,'registers':{n:hex(v) for n,v in regs.items()},
               'caller':hex(stack[0]),'arguments':[hex(v) for v in stack[1:]]}
        try:
            # Pinned NT5 x86 KPCR/KTHREAD; EPROCESS offsets come from its PDB.
            thread=read32(0xffdff124);process=read32(thread+0x44)
            image=g.read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii')
            pid=read32(process+fields['UniqueProcessId']['offset'])
            event.update(image=image,pid=pid,thread=hex(thread),process=hex(process))
            peb=read32(process+fields['Peb']['offset'])
            params=read32(peb+0x10)
            length,maximum,buffer=struct.unpack('<HHI',g.read(params+0x40,8))
            assert length<=maximum and length<=4096 and length%2==0
            event['command_line']=g.read(buffer,length).decode('utf-16le')
        except Exception as exc:event['process_decode_error']=repr(exc)
        report['events'].append(event);save()
        # Step over the restored instruction before rearming this entry.
        g.bp(target,False);armed.remove(target);assert g.ask('s').startswith(('T','S'))
        g.bp(target);armed.add(target)
    report['status']='bounded_capture_complete'
except Exception as exc:
    report['status']='capture_incomplete';report['error']=repr(exc)
finally:
    if g:
        try:
            if report.get('status')=='capture_incomplete':g.s.settimeout(5);g.interrupt()
            for target in list(armed):g.bp(target,False);armed.remove(target)
            g.send('c');report['guest_resumed']=True
        except Exception as exc:
            report['resume_error']=repr(exc)
            try:command(4594,'cont');report['monitor_resumed']=True
            except Exception as fallback:report['monitor_resume_error']=repr(fallback)
        g.s.close()
    lock.close();save()
print(json.dumps(report,indent=2))
