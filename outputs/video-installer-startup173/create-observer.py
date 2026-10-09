"""Construct bounded successor observer before freezing; old trace remains intact."""
import ast
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'video-process-lifecycle169/trace.py').read_text(encoding='utf-8')
s=s.replace('video-process-lifecycle169','video-installer-startup173').replace('vlife169','vstart173')
# Reuse proven GDB, IDT, string, owner and single-step utilities, not the old loop.
s=s[:s.index('try:\n    command(4594,\'stop\')')]
s=s.replace("sites={v['address']:v for v in review['sites'] if v['module']!='ntoskrnl.exe'};armed=set();pending={};g=None;stopped=False;kernel=None",
            "sites={v['address']:v for v in review['sites'] if v['module']!='ntoskrnl.exe'};armed=set();pending={};g=None;stopped=False;kernel=None;shutdown_seen=False")
begin=s.index('    if name!=\'ntoskrnl.exe\':',s.index('def pin('))
end=s.index('    while True:',begin)
s=s[:begin]+'''    found=None;loader_error=None
    if name!='ntoskrnl.exe':
        try:
            found=module_at(site['address'],who)
            assert found and found['name']==name and found['base']==base and found['size']==((pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
        except Exception as exc:
            loader_error=repr(exc);found=None
    else:found=dict(name=name,base=kernel,size=pe.OPTIONAL_HEADER.SizeOfImage)
    header={}
    try:
        assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096
        assert g.read(base+nt,4)==b'PE\\0\\0'
        assert u32(base+nt+8)==pe.FILE_HEADER.TimeDateStamp
        assert u32(base+nt+80)==pe.OPTIONAL_HEADER.SizeOfImage
        header=dict(readable=True,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
    except AssertionError as exc:
        if not found or name=='ntoskrnl.exe' or str(exc)!='E14':raise
        header=dict(readable=False,reason='Header nonresident; require actual loader identity AND exact relocated resident bytes')
    if not found:
        assert header.get('readable')
        found=dict(name=name,base=base,size=pe.OPTIONAL_HEADER.SizeOfImage,identity='PE metadata plus relocated resident bytes',loader_unknown=loader_error)
''' + s[end:]
insert=s.index('def pin(')
s=s[:insert]+'''def module_at(address,who):
    peb=u32(who['process']+fields['Peb']['offset']);assert 0x10000<=peb<0x80000000
    ldr=u32(peb+12);assert 0x10000<=ldr<0x80000000
    head=ldr+12;q=u32(head);seen=set()
    while q!=head:
        assert q and q not in seen and len(seen)<100;seen.add(q)
        base,size=u32(q+24),u32(q+32)
        if base<=address<base+size:
            length,maximum,p=struct.unpack('<HHI',g.read(q+44,8));assert length<=maximum and length<=512
            label=g.read(p,length).decode('utf-16le').lower() if length else ''
            return dict(base=base,size=size,name=label)
        q=u32(q)
    return None
def caller_pin(address,who):
    row=module_at(address,who)
    if not row:return dict(unknown='Address not in current loader inventory')
    if row['name'] not in pes:return dict(module=row,unknown='Cold binary not pinned; no attribution beyond loader inventory')
    pe=pes[row['name']];rva=address-row['base']
    site=dict(module=row['name'],name='actual_return_caller',address=address,rva=rva,validation_bytes=pe.get_data(rva,32).hex())
    return dict(module=row,pin=pin(site,who))
def last_error(who):
    teb=u32(who['thread']+review['teb_offset']);assert 0x10000<=teb<0x80000000
    return dict(teb=teb,last_error=u32(teb+review['last_error_offset']))

''' + s[insert:]
s+='''try:
    command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for a in sites:arm(a)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+360
    for hit in range(1024):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in read(launch).get('cycles',[]))
                stop_requested=(out/'trace-stop.signal').exists()
                if returned or stop_requested or time.monotonic()>=deadline:
                    g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_observed' if returned else ('supervisor_stop' if stop_requested else 'capture_deadline');break
        stopped=True;g.s.settimeout(5)
        if r['status'] in ['dashboard_observed','supervisor_stop','capture_deadline']:break
        cpu=regs();a=cpu['EIP'];assert a in armed,(reply,cpu);kernel_identity();who=owner();site=sites.get(a)
        try:
            index=pin(site,who) if site else None
            if site is None:
                calls=[v for v in pending.get((who['thread'],a),[]) if cpu['ESP']==v['stack']+v['stack_delta']]
                assert len(calls)==1,'Return must match exact thread AND stdcall stack'
                call=calls[0];assert g.read(a,len(bytes.fromhex(call['return_bytes']))).hex()==call['return_bytes']
        except AssertionError as exc:
            if str(exc)!='E14':raise
            r['unreadable_hits'].append(dict(address=a,owner=who,utc=utc(),site=site['name'] if site else 'return',reason='E14; no data/call inferred'))
            assert len(r['unreadable_hits'])<=32
            remove(a);step();arm(a);save();continue
        event=dict(index=len(r['events']),utc=utc(),tick_count=u32(kernel+pubs['_KeTickCount']['rva']),owner=describe(who),registers=cpu,pin=index,after_shutdown_entry=shutdown_seen)
        if site:
            args=struct.unpack('<'+'I'*(site['argc']+1),g.read(cpu['ESP'],4*(site['argc']+1)))
            event.update(function=site['name'],kind=site['kind'],caller=args[0],arguments=list(args[1:]))
            if site['kind'] in ['create_inner','create_outer']:
                for label,p in [('command_line',args[3]),('application',args[2])]:
                    try:event[label]=wide(p)
                    except Exception as exc:event[label+'_unknown']=repr(exc)
                ret=args[0];assert 0x10000<=ret<0x80000000
                try:event['caller_identity']=caller_pin(ret,who)
                except Exception as exc:event['caller_identity_unknown']=repr(exc)
                call=dict(entry_index=event['index'],function=site['name'],thread=who['thread'],parent_pid=who['pid'],stack=cpu['ESP'],stack_delta=48,
                    return_address=ret,return_bytes=g.read(ret,16).hex(),process_info=args[11],command_line=event.get('command_line'),application=event.get('application'),returned=False)
                pending.setdefault((who['thread'],ret),[]).append(call);arm(ret);event['creation_flags']=args[7]
            elif site['kind']=='harderror':
                event['status']=hex(args[1])
                count,mask,ptr=args[2:5]
                try:
                    assert count<=8
                    values=list(struct.unpack('<'+'I'*count,g.read(ptr,4*count))) if count else []
                    event['harderror_parameters']=values;event['unicode_parameters']={}
                    for i,value in enumerate(values):
                        if mask&(1<<i):
                            n,m,p=struct.unpack('<HHI',g.read(value,8));assert n<=m and n<=4096 and n%2==0
                            event['unicode_parameters'][str(i)]=g.read(p,n).decode('utf-16le',errors='backslashreplace') if n else ''
                except Exception as exc:event['parameters_unknown']=repr(exc)
            elif site['kind']=='shutdown':shutdown_seen=True;r['shutdown_entry_observed']=True
        else:
            call.update(returned=True,result=cpu['EAX']);pending[(who['thread'],a)].remove(call)
            event.update(function=call['function']+'_return',entry_index=call['entry_index'],return_eax=cpu['EAX'],call=call)
            try:event.update(last_error(who))
            except Exception as exc:event['last_error_unknown']=repr(exc)
            if cpu['EAX'] and call['process_info']:
                try:event['process_information']=list(struct.unpack('<4I',g.read(call['process_info'],16)))
                except Exception as exc:event['process_information_unknown']=repr(exc)
        assert len(r['events'])<1024;r['events'].append(event);save()
        remove(a);step()
        if a in sites or any(addr==a and vals for (_,addr),vals in pending.items()):arm(a)
    else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc),host_traceback=traceback.format_exc())
finally:
    r['pending_returns']=[v for vals in pending.values() for v in vals]
    r['breakpoints_before_teardown']=sorted(armed)
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for a in list(armed):remove(a)
            r['breakpoints_after_teardown']=sorted(armed);g.send('c');r['guest_resumed']=True
        except Exception as exc:
            r['teardown_error']=repr(exc)
            try:command(4594,'cont');r['monitor_resumed']=True
            except Exception as fallback:r['monitor_resume_error']=repr(fallback)
        g.s.close()
    elif stopped:command(4594,'cont')
    r['ended_utc']=utc();save();lock.close();(out/'trace-closed.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['status','error','guest_resumed'] if n in r}));print('events',len(r['events']))
'''
ast.parse(s);assert 'actual_creation_caller' not in s and 'vstart173' in s
(k/'trace.py').write_bytes(s.encode('utf-8'))
print('173 observer constructed; no launch')
