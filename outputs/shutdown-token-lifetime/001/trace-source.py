"""Observe saved PnP token lifetime and native query returns; debugger evidence only."""
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
run=ws/('work/runs/nt5-shutdown-token-lifetime-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
capture=sys.argv[2] if len(sys.argv)>2 else 'trace.json';assert capture in ['trace.json','trace-retry.json','trace-paging.json'];assert not (out/capture).exists()
layout=json.loads((src/'process-layouts.json').read_text());fields=layout['_EPROCESS']['fields']
pubs=json.loads((src/'kernel-publics.json').read_text())['symbols']
review=json.loads((k/'site-review.json').read_text());base=int(state['kernel_base'],16)
targets={(base+s['rva'] if s['module']=='ntoskrnl.exe' else s['address']):s for s in review['sites']}
report=dict(scope=__doc__,physical_access=False,ordinary_boot_qualified=False,events=[],sites=review,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
report['active_sites']={hex(a):s['name'] for a,s in targets.items()}
report['trace_source_sha256']=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest()
g=None;armed=set();lock=acquire_monitor_lock(4594);stopped=False
def save(): (out/capture).write_text(json.dumps(report,indent=2)+'\n')
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

def wide(p):
    if not p:return ''
    assert 0x10000<=p<0x80000000
    raw=bytearray()
    for n in range(2048):
        part=g.read(p+2*n,2)
        if part==b'\0\0':return raw.decode('utf-16le')
        raw.extend(part)
    raise ValueError('Unterminated command')

def token_state():
    result={}
    for name,address in [('saved_token',review['token_global']),('saved_mutex',review['mutex_global'])]:
        try:result[name]=hex(u32(address))
        except Exception as exc:result[name+'_read_error']=repr(exc)
    return result

pending={};verified=set();report['ignored_hits']=0
try:
    command(4594,'stop');stopped=True
    g=Remote(4595);report['gdb_features']=g.ask('qSupported');report['initial_stop']=g.ask('?')
    for address,site in targets.items():
        if site['module']=='ntoskrnl.exe':assert g.read(address,len(bytes.fromhex(site['bytes']))).hex()==site['bytes']
        if site['kind'] not in ['token_return','duplicate_return','setinfo_return']:g.bp(address);armed.add(address)
    save();deadline=time.monotonic()+360
    while len(report['events'])<512 and time.monotonic()<deadline:
        g.send('c');stopped=False;g.s.settimeout(max(1,deadline-time.monotonic()));response=g.recv();stopped=True;g.s.settimeout(5)
        packet=bytes.fromhex(g.ask('g'));values=struct.unpack('<9I',packet[:36]);regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],values))
        address=regs['EIP'];assert address in armed,(response,regs)
        try:g.read(address,3)
        except AssertionError as exc:
            if str(exc)!='E14':raise
            report.setdefault('unreadable_site_hits',[]).append(dict(address=hex(address),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
            save();g.bp(address,False);armed.remove(address);assert g.ask('s').startswith(('T','S'))
            g.bp(address);armed.add(address);continue
        thread=u32(0xffdff124);process=u32(thread+review['thread_owner_offset'])
        image=g.read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace')
        site=targets.get(address);matched=pending.get((thread,address))
        is_services=image.lower()=='services.exe'
        active=any(t==thread for t,_ in pending)
        saved=token_state() if is_services else {}
        interested=True
        if site and site['kind']=='close':
            interested=is_services and saved.get('saved_token') not in [None,'0x0'] and hex(u32(regs['ESP']+4))==saved['saved_token']
        if site and site['kind']=='create':
            interested=is_services and (active or (site['name']=='CreateProcessAsUserW' and u32(regs['ESP'])==0x767a66de))
        event=None
        if matched:
            call=matched.pop();event=dict(function=call['function']+'_return',entry_index=call['entry_index'],command_line=call['command_line'],return_eax=hex(regs['EAX']),saved_return=hex(address))
            assert g.read(address,len(bytes.fromhex(call['return_bytes']))).hex()==call['return_bytes']
            if not matched:del pending[(thread,address)]
            if regs['EAX'] and call['process_info']:
                event['process_information']=[hex(v) for v in struct.unpack('<4I',g.read(call['process_info'],16))]
        elif site:
            assert g.read(address,len(bytes.fromhex(site['bytes']))).hex()==site['bytes'],site
            verified.add(address)
            if site['kind'] in ['harderror','shutdown'] or (is_services and interested and (site['kind'] not in ['token_return','duplicate_return','setinfo_return','terminate','csr'] or active)):
                argc=site['argc'];args=struct.unpack('<'+str(argc+1)+'I',g.read(regs['ESP'],4*(argc+1)))
                event=dict(function=site['name'],caller=hex(args[0]),arguments=[hex(v) for v in args[1:]],eax=hex(regs['EAX']))
                if site['kind']=='pnp':
                    event.pop('caller');event.pop('arguments')
                    event['registers']={name:hex(value) for name,value in regs.items()}
                    event['stack_words']=[hex(v) for v in struct.unpack('<6I',g.read(regs['ESP'],24))]
                if site['kind']=='close':
                    ret=args[0];assert 0x10000<=ret<0x80000000
                    entry=dict(function=site['name'],command_line='',entry_index=len(report['events']),process_info=0,return_bytes=g.read(ret,3).hex())
                    pending.setdefault((thread,ret),[]).append(entry)
                    if ret not in armed:g.bp(ret);armed.add(ret)
                if site['kind']=='create':
                    event['creation_flags']=hex(args[7])
                    for key,pointer in [('command_line',args[3]),('application',args[2])]:
                        try:event[key]=wide(pointer)
                        except Exception as exc:event[key+'_decode_error']=repr(exc)
                    event.setdefault('command_line','')
                    ret=args[0];assert 0x10000<=ret<0x80000000
                    entry=dict(function=site['name'],command_line=event['command_line'],entry_index=len(report['events']),process_info=args[11],return_bytes=g.read(ret,3).hex())
                    pending.setdefault((thread,ret),[]).append(entry)
                    if ret not in armed:g.bp(ret);armed.add(ret)
                    for a,extra in targets.items():
                        if extra['kind'] in ['token_return','duplicate_return','setinfo_return'] and a not in armed:g.bp(a);armed.add(a)
                elif site['kind']=='csr':
                    event['stack_top_at_interior_site']=event.pop('caller')
                    event['caller']=hex(u32(regs['EBP']+4))
                    event['csr_message_status']=hex(u32(regs['EBP']-0x2b0));event['new_process_handle']=hex(u32(regs['EBP']-0x178))
                if site['kind'] in ['terminate','setinfo_return','csr','token_return','duplicate_return']:
                    event['active_creations']=[item for (t,_),items in pending.items() if t==thread for item in items]
        if event:
            if is_services:event.update(saved)
            event.update(index=len(report['events']),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),thread=hex(thread),owner=describe(process),tick_count=u32(base+pubs['_KeTickCount']['rva']))
            try:
                teb=u32(thread+review['teb_offset']);event['last_error']=u32(teb+0x34)
            except Exception as exc:event['last_error_decode_error']=repr(exc)
            report['events'].append(event);save()
        else:report['ignored_hits']+=1
        if not pending:
            for a,extra in targets.items():
                if extra['kind'] in ['token_return','duplicate_return','setinfo_return'] and a in armed and a!=address:g.bp(a,False);armed.remove(a)
        if site and site['kind']=='shutdown':report['status']='reached_kernel_shutdown';break
        g.bp(address,False);armed.remove(address);assert g.ask('s').startswith(('T','S'))
        if (address in targets and (targets[address]['kind'] not in ['token_return','duplicate_return','setinfo_return'] or pending)) or any(a==address for _,a in pending):g.bp(address);armed.add(address)
    else:report['status']='bounded_capture_limit'
except Exception as exc:report.update(status='capture_incomplete',error=repr(exc),host_traceback=__import__('traceback').format_exc())
finally:
    report['verified_live_sites']=[dict(address=hex(a),name=targets[a]['name']) for a in sorted(verified)]
    report['pending_returns']=[dict(thread=hex(t),address=hex(a),calls=items) for (t,a),items in pending.items()]
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
