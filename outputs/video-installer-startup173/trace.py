"""Bounded process creation/hard-error observation. Read only; debugger evidence."""
import datetime,hashlib,json,socket,struct,sys,time,traceback
from pathlib import Path
from atomic_json import write_json
from discover_kernel import discover
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001';run=ws/'work/runs/nt5-vstart173-candidate001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
review=read(k/'sites.json');fields=read(k.parent/'native-windows-nt5-kernel/process-layouts.json')['_EPROCESS']['fields']
for path,digest in review['dependency_pins'].items():assert sha(ws/path)==digest,path
assert sha(k.parent/'native-windows-nt5-kernel/process-layouts.json')==review['layouts_sha256']
assert sha(k.parent/'native-windows-nt5-kernel/kernel-publics.json')==review['publics_sha256']
pubs=read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols']
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
pes={}
for name,row in review['binaries'].items():
    p=ws/row['path'];assert sha(p)==row['sha256'];pes[name]=pefile.PE(str(p))
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
# User entry is the sole initial address lead. Kernel virtual bases differ from
# hardware; discover the actual pinned image before deriving any kernel site.
sites={v['address']:v for v in review['sites'] if v['module']!='ntoskrnl.exe'};armed=set();pending={};g=None;stopped=False;kernel=None;shutdown_seen=False
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__)),
    sites_sha256=sha(k/'sites.json'),events=[],pins=[],unreadable_hits=[],single_steps=[],pending_returns=[],guest_data_or_register_writes=False)
lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def regs():return dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP','EFLAGS'],struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
def owner():
    thread=u32(0xffdff124);process=u32(thread+review['thread_owner_offset'])
    return dict(thread=thread,process=process,pid=u32(process+fields['UniqueProcessId']['offset']),
        image=g.read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'))
def wide(p,limit=4096):
    if not p:return ''
    assert 0x10000<=p<0x80000000 and limit<=4096
    data=bytearray()
    while len(data)<limit:
        n=min(64,limit-len(data),4096-((p+len(data))%4096));assert n%2==0
        data.extend(g.read(p+len(data),n))
        for i in range(len(data)-n,len(data),2):
            if data[i:i+2]==b'\0\0':return bytes(data[:i]).decode('utf-16le',errors='backslashreplace')
    raise ValueError('Unterminated bounded UTF16 string')
def describe(who):
    row=dict(who)
    try:
        peb=u32(who['process']+fields['Peb']['offset']);assert 0x10000<=peb<0x80000000
        params=u32(peb+0x10);flags=u32(params+8);n,m,p=struct.unpack('<HHI',g.read(params+0x40,8))
        assert n<=m and n<=4096 and n%2==0
        if not flags&1 and p:p+=params
        row.update(peb=peb,parameters=params,parameter_flags=flags,command_line=g.read(p,n).decode('utf-16le',errors='backslashreplace') if n else '')
    except Exception as exc:row['command_unknown']=repr(exc)
    return row
def kernel_identity():
    global kernel
    if kernel is None:
        kernel,evidence=discover(g.read,command(4594,'info registers'),pes['ntoskrnl.exe'],pubs)
        r['kernel_identity']=evidence
        r['kernel_static_lead']=review['kernel_base_expected']
        for original in review['sites']:
            if original['module']=='ntoskrnl.exe':
                site=dict(original,address=kernel+original['rva'])
                sites[site['address']]=site;arm(site['address'])
        r['runtime_sites']={hex(a):v for a,v in sites.items()};save()
def module_at(address,who):
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

def pin(site,who):
    name=site['module'];pe=pes[name];base=site['address']-site['rva'];n=32
    found=None;loader_error=None
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
        assert g.read(base+nt,4)==b'PE\0\0'
        assert u32(base+nt+8)==pe.FILE_HEADER.TimeDateStamp
        assert u32(base+nt+80)==pe.OPTIONAL_HEADER.SizeOfImage
        header=dict(readable=True,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
    except AssertionError as exc:
        if not found or name=='ntoskrnl.exe' or str(exc)!='E14':raise
        header=dict(readable=False,reason='Header nonresident; require actual loader identity AND exact relocated resident bytes')
    if not found:
        assert header.get('readable')
        found=dict(name=name,base=base,size=pe.OPTIONAL_HEADER.SizeOfImage,identity='PE metadata plus relocated resident bytes',loader_unknown=loader_error)
    while True:
        rel=[e.rva-site['rva'] for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]) for e in block.entries if e.type==3 and site['rva']<=e.rva<site['rva']+n]
        end=max([n]+[v+4 for v in rel]);assert end<=64
        if end==n:break
        n=end
    raw=pe.get_data(site['rva'],n);assert raw[:32].hex()==site['validation_bytes'];data=bytearray(raw)
    for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    actual=g.read(site['address'],n);assert actual==data,(name,hex(site['rva']),'Resident code mismatch')
    row=dict(module=found,header=header,site=site['name'],address=site['address'],rva=site['rva'],raw=raw.hex(),resident=actual.hex(),relocations=rel,source_sha256=review['binaries'][name]['sha256'])
    r['pins'].append(row);return len(r['pins'])-1
def remove(a):
    if a in armed:g.bp(a,False);armed.remove(a)
def arm(a):
    if a not in armed:g.bp(a);armed.add(a)
def step():
    for attempt in range(4):
        before=regs();own=owner();reply=g.ask('s');assert reply.startswith(('T','S'));after=regs();new=owner()
        unchanged=before==after and own==new
        r['single_steps'].append(dict(before=before,after=after,before_owner=own,after_owner=new,reply=reply,attempt=attempt,unchanged=unchanged))
        assert len(r['single_steps'])<=4096
        if not unchanged:return
    raise RuntimeError('No observed step progress in4 bounded attempts')
try:
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
