"""Bounded read-only observations of NT5 dump initialization in one owned emulator."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='serial003'
out=k/case;run=ws/('work/runs/nt5-dump-config-trace-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();review=json.loads((k/'sites-v3.json').read_text())
for name,digest in review['dependencies'].items():assert sha(k.parent/name)==digest
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
P=json.loads((k.parent/'native-windows-nt5-kernel/process-layouts.json').read_text())['_EPROCESS']['fields']
owner=json.loads((k.parent/'shutdown-popup-workload/site-review.json').read_text())['thread_owner_offset']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__)),sites_sha256=sha(k/'sites-v3.json'),events=[],calls=[],hit_counts={})
g=None;stopped=False;armed=set();pending={};completed={};outer={};dump={};sites={s['address']:s for s in review['sites']};lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def who(t):
    proc=u32(t+owner)
    return dict(thread=hex(t),process=hex(proc),pid=u32(proc+P['UniqueProcessId']['offset']),image=g.read(proc+P['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'))
def reg():return dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
def optional(row,label,a,n):
    try:row[label]=g.read(a,n).hex()
    except Exception as exc:row[label+'_unreadable']=dict(address=hex(a),length=n,error=repr(exc))
try:
    command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for a in sites:g.bp(a);armed.add(a)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+600
    for hit in range(128):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in json.loads(launch.read_text()).get('cycles',[]))
                if returned or time.monotonic()>=deadline:
                    g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_observed' if returned else 'capture_deadline';break
        stopped=True;g.s.settimeout(5)
        if r['status'] in ['dashboard_observed','capture_deadline']:break
        regs=reg();a=regs['EIP'];assert a in sites,(hex(a),reply);site=sites[a];name=site['name']
        K=review['kernel_base_expected'];assert g.read(K,2)==b'MZ' and u32(K+u32(K+60)+8)==review['kernel_timestamp']
        assert g.read(a,len(bytes.fromhex(site['relocated']))).hex()==site['relocated'],(name,'resident code mismatch')
        thread=u32(0xffdff124);row=dict(index=len(r['events']),kind=name,utc=utc(),resident_bytes=site['relocated'],registers={n:hex(v) for n,v in regs.items()},**who(thread))
        r['events'].append(row);r['hit_counts'][name]=r['hit_counts'].get(name,0)+1;save()
        if name=='configure_entry':
            assert thread not in outer
            outer[thread]=dict(entry_stack=regs['ESP'],frame=regs['ESP']-4,handle=hex(u32(regs['ESP']+4)))
            row['configure']=outer[thread]
        elif name in ['configure_handle_return','dump_stack_return','allocate_call','allocate_return','no_memory','complete_call','caller_status','caller_error']:
            cfg=outer[thread];assert regs['EBP']==cfg['frame'],'Configure frame mismatch'
            row['configure_entry_stack']=hex(cfg['entry_stack'])
            row['status_or_pointer']=hex(regs['EAX'])
            if name=='allocate_call':row['arguments']=[hex(v) for v in struct.unpack('<III',g.read(regs['ESP'],12))]
            if name=='configure_handle_return':row['file_object_out']=hex(u32(regs['EBP']-4))
            if name=='caller_status':
                assert regs['ESP']==cfg['entry_stack']-16
                if thread in completed:
                    call=completed[thread];assert regs['ESP']==int(call['entry_stack'],16)+8 and a==int(call['return_address'],16)
                    row['paired_complete_call']=call['index']
                else:row['complete_initialization_not_entered']=True
            if name=='caller_error':
                assert regs['ESP']==cfg['entry_stack']-32 and regs['EAX']>=0x80000000
                row['event_id']='0xc0040031'
        elif name=='stack_entry':
            assert thread not in dump
            dump[thread]=dict(stack=regs['ESP'],frame=regs['ESP']-4,return_address=u32(regs['ESP']))
            row['stack_call']=dump[thread];row['arguments']=[hex(v) for v in struct.unpack('<6I',g.read(regs['ESP']+4,24))]
        elif name.startswith('stack_'):
            dc=dump[thread];frame=dc['frame']
            if name=='stack_final_return':
                assert regs['ESP']==dc['stack'];row['status']=hex(regs['EAX']);row['paired_return_address']=hex(dc['return_address'])
            else:
                assert regs['EBP']==frame,'Dump stack frame mismatch'
                row['status_or_pointer']=hex(regs['EAX']);optional(row,'iosb',frame-0x20,8)
                if name.endswith('_call') and name!='stack_driver_call':
                    count=6 if name=='stack_open_call' else 9 if name=='stack_build_call' else 10
                    args=struct.unpack('<'+'I'*count,g.read(regs['ESP'],4*count));row['arguments']=[hex(v) for v in args]
                if name=='stack_driver_call':
                    row.update(device_object=hex(regs['ECX']),irp=hex(regs['EDX']))
                    layouts=json.loads((k.parent/'native-windows-nt5-kernel/pnp-layouts.json').read_text())
                    dev=regs['ECX'];drv=u32(dev+layouts['_DEVICE_OBJECT']['fields']['DriverObject']['offset']);df=layouts['_DRIVER_OBJECT']['fields']
                    length,maximum,buffer=struct.unpack('<HHI',g.read(drv+df['DriverName']['offset'],8));assert length<=maximum and length<=512
                    row['driver']=dict(address=hex(drv),name=g.read(buffer,length).decode('utf-16le'),base=hex(u32(drv+df['DriverStart']['offset'])),size=u32(drv+df['DriverSize']['offset']))
                    optional(row,'irp_prefix',regs['EDX'],112)
                if name=='stack_driver_effective':
                    row['effective_status']=hex(u32(frame-4));optional(row,'dump_pointers',regs['EDI'],40)
                if name=='stack_no_name':row['dump_driver_name_pointer']=hex(u32(frame-0x14))
        elif name=='entry':
            stack=regs['ESP'];assert thread not in pending
            call=dict(index=len(r['calls']),thread=hex(thread),entry_stack=hex(stack),frame=hex(stack-4),handle=hex(u32(stack+4)),return_address=hex(u32(stack)),event_indices=[])
            r['calls'].append(call);pending[thread]=call;row['call_index']=call['index']
        else:
            call=pending[thread];row['call_index']=call['index']
            if name=='return':
                assert regs['ESP']==int(call['entry_stack'],16)
                call.update(status=hex(regs['EAX']),completed=True);completed[thread]=pending.pop(thread)
            else:
                assert regs['EBP']==int(call['frame'],16),'Frame mismatch'
                frame=regs['EBP']
                if name=='handle_return':
                    row['status']=hex(regs['EAX']);row['file_object_out']=hex(u32(frame-4))
                    if regs['EAX']<0x80000000 and u32(frame-4):optional(row,'file_object_prefix',u32(frame-4),96)
                if name.endswith('call'):
                    count=5 if name=='query_call' else 10
                    row['arguments']=[hex(v) for v in struct.unpack('<'+'I'*count,g.read(regs['ESP'],4*count))]
                if name.startswith(('query_','fsctl_')) and not name.endswith('call'):
                    row['status']=hex(regs['EAX']) if 'pending' not in name else hex(u32(frame-0x1c))
                    optional(row,'iosb',frame-0x1c,8)
                    if name.startswith('query_'):optional(row,'standard_information',frame-0x34,24)
                    else:optional(row,'retrieval_pointer_out',frame-0xc,4)
        if 'call_index' in row:r['calls'][row['call_index']]['event_indices'].append(row['index'])
        save()
        g.bp(a,False);armed.remove(a);assert g.ask('s').startswith(('T','S'));g.bp(a);armed.add(a)
        if name=='caller_error':r['status']='failure_path_captured';break
        if time.monotonic()>=deadline:r['status']='capture_deadline';break
    else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc))
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for a in list(armed):g.bp(a,False);armed.remove(a)
            g.send('c');r['guest_resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
        g.s.close()
    elif stopped:command(4594,'cont')
    r.update(ended_utc=utc(),pending_calls=len(pending),armed_breakpoints_remaining=[hex(a) for a in armed]);save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','hit_counts','guest_resumed','pending_calls'] if n in r},indent=2))
