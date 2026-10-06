"""Bounded debugger-interrupted installer lifecycle capture; not boot qualification."""
import datetime,json,re,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002'];out=k/case
src=ws/'outputs/native-windows-nt5-kernel'
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
namespace={};code=(src/'trace-entry.py').read_text()
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),namespace)
Remote=namespace['Remote'];state=json.loads((out/'runtime.json').read_text())
assert state['status'] in ['shell_running','kernel_running']
run=ws/('work/runs/nt5-shutdown-installer-trace-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
assert not (out/'trace.json').exists()
layout=json.loads((src/'process-layouts.json').read_text());fields=layout['_EPROCESS']['fields']
pubs=json.loads((src/'kernel-publics.json').read_text())['symbols']
review=json.loads((k/'site-review.json').read_text());base=int(state['kernel_base'],16)
targets={base+s['rva']:s for s in review['sites']}
report=dict(scope=__doc__,physical_access=False,ordinary_boot_qualified=False,events=[],sites=review,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
report['trace_source_sha256']=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest()
g=None;armed=set();lock=acquire_monitor_lock(4594);stopped=False
def save(): (out/'trace.json').write_text(json.dumps(report,indent=2)+'\n')
def u32(p):return struct.unpack('<I',g.read(p,4))[0]
def target_command(process):
    peb=u32(process+fields['Peb']['offset'])
    cr3=u32(process+fields['Pcb']['offset']+layout['_KPROCESS']['fields']['DirectoryTableBase']['offset'])
    assert peb>=0x10000 and peb<0x80000000,'No user PEB'
    assert g.ask('Qqemu.PhyMemMode:1')=='OK'
    try:
        def physical32(p):
            assert 0<=p<0x4000000-3
            return u32(p)
        def read(va,size):
            assert 0<=size<=4096 and 0x10000<=va and va+size<=0x80000000
            result=b''
            while size:
                pde=physical32((cr3&0xfffff000)+4*(va>>22));assert pde&1,'Nonresident target PDE'
                if pde&128:pa=(pde&0xffc00000)+(va&0x3fffff)
                else:
                    pte=physical32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1,'Nonresident target PTE'
                    pa=(pte&0xfffff000)+(va&4095)
                n=min(size,4096-(va&4095));assert pa+n<=0x4000000
                result+=g.read(pa,n);va+=n;size-=n
            return result
        params=struct.unpack('<I',read(peb+0x10,4))[0]
        flags=struct.unpack('<I',read(params+8,4))[0]
        length,maximum,buffer=struct.unpack('<HHI',read(params+0x40,8))
        assert length<=maximum and length<=4096 and length%2==0
        raw_buffer=buffer
        if not flags&1 and buffer:buffer+=params
        return dict(command_line=read(buffer,length).decode('utf-16le') if length else '',parameters_flags=hex(flags),parameters=hex(params),raw_command_buffer=hex(raw_buffer),resolved_command_buffer=hex(buffer))
    finally:assert g.ask('Qqemu.PhyMemMode:0')=='OK'
def describe(process):
    row=dict(eprocess=hex(process))
    try:
        row.update(image=g.read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'),pid=u32(process+fields['UniqueProcessId']['offset']))
        row.update(target_command(process))
    except Exception as exc:row['decode_error']=repr(exc)
    return row
try:
    command(4594,'stop');stopped=True
    g=Remote(4595);report['gdb_features']=g.ask('qSupported');report['initial_stop']=g.ask('?')
    # Verify code before arming. No guest registers, arguments or data are changed.
    for address,site in targets.items():
        actual=g.read(address,len(bytes.fromhex(site['bytes']))).hex();assert actual==site['bytes'],(site,actual)
    report['live_site_bytes_verified']=True
    for address in targets:g.bp(address);armed.add(address)
    save();deadline=time.monotonic()+360
    while len(report['events'])<512 and time.monotonic()<deadline:
        g.send('c');stopped=False;g.s.settimeout(max(1,deadline-time.monotonic()));response=g.recv();stopped=True;g.s.settimeout(5)
        # i386 GDB register packet order: EAX ECX EDX EBX ESP EBP ESI EDI EIP.
        packet=bytes.fromhex(g.ask('g'));values=struct.unpack('<9I',packet[:36]);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],values))
        address=regs['EIP'];assert address in targets,(response,regs)
        site=targets[address];argc=site['argc'];at=regs['EBP']+4 if site['frame']=='ebp' else regs['ESP']
        args=struct.unpack('<'+str(argc+1)+'I',g.read(at,4*(argc+1)))
        event=dict(index=len(report['events']),function=site['name'],utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),caller=hex(args[0]),arguments=[hex(v) for v in args[1:]])
        try:
            thread=u32(0xffdff124);event['owner']=describe(u32(thread+review['thread_owner_offset']))
            event['thread']=hex(thread);event['tick_count']=u32(base+pubs['_KeTickCount']['rva'])
            if site['name']=='NtTerminateProcess_AfterReference':event['target']=describe(u32(regs['EBP']-8))
            elif site['name']=='NtResumeThread_BeforeResume':
                t=u32(regs['EBP']-0x24);event['target_thread']=hex(t);event['target']=describe(u32(t+review['thread_owner_offset']))
            elif site['name']=='_PspExitProcess@8':event['target']=describe(args[2])
        except Exception as exc:event['decode_error']=repr(exc)
        report['events'].append(event);save()
        if site['name']=='_NtShutdownSystem@4':
            report['status']='reached_kernel_shutdown';break
        g.bp(address,False);armed.remove(address);assert g.ask('s').startswith(('T','S'))
        g.bp(address);armed.add(address)
    else:report['status']='bounded_capture_limit'
except Exception as exc:report.update(status='capture_incomplete',error=repr(exc))
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for address in list(armed):g.bp(address,False);armed.remove(address)
            g.send('c');report['guest_resumed']=True
        except Exception as exc:
            report['resume_error']=repr(exc)
            try:command(4594,'cont');report['monitor_resumed']=True
            except Exception as fallback:report['monitor_resume_error']=repr(fallback)
        g.s.close()
    elif stopped:command(4594,'cont')
    report['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();lock.close()
print(json.dumps({n:report[n] for n in ['status','error','guest_resumed'] if n in report}));print('events',len(report['events']))
