"""Bounded read-only successful dump mapping trace with an independent cold oracle."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='trace001'
out=k/case;run=ws/('work/runs/nt5-dump-map-trace-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
review=read(k/'sites.json');mods=read(k/'modules.json');L=read(k/'layouts.json')['structures'];K=review['kernel_base_expected'];oracle=read(k/'cold-oracle.json')
for n,d in review['dependencies'].items():assert sha(k.parent/n)==d
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
pes={}
for n,m in mods.items():assert sha(Path(m['path']))==m['sha256'];pes[n]=pefile.PE(m['path'])
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
owner=read(k.parent/'shutdown-popup-workload/site-review.json')['thread_owner_offset'];utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__)),input_sha256={n:sha(k/n) for n in ['sites.json','modules.json','layouts.json','cold-oracle.json']},events=[],runtime_pins=[],calls=[],fatx_calls=[],module_list=[])
g=None;stopped=False;armed=set();loaded=[];outer={};dump={};pending={};completed={};returns={};fsargs=None
sites={s['address']:dict(s) for s in review['sites']};lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def field(t,n):return L[t]['fields'][n]['offset']
def uni(a):
    n,maximum,p=struct.unpack('<HHI',g.read(a,8));assert n<=maximum and n<=2048;return g.read(p,n).decode('utf-16le') if n else ''
def who():
    t=u32(0xffdff124);p=u32(t+owner);return dict(thread=hex(t),process=hex(p),pid=u32(p+field('_EPROCESS','UniqueProcessId')),image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'))
def modules():
    head=K+review['loaded_module_list_rva'];q=u32(head);rows=[];seen=set()
    while q!=head:
        assert q and q not in seen and len(seen)<200;seen.add(q);node=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
        rows.append(dict(base=u32(node+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(node+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(node+field('_LDR_DATA_TABLE_ENTRY','BaseDllName'))));q=u32(q)
    return rows
def pin(a,n=16):
    m=next(v for v in loaded if v['base']<=a<v['base']+v['size']);name=m['name'].lower();p=pes[name];base=m['base'];rva=a-base
    assert m['size']==((mods[name]['image_size']+4095)&~4095)
    assert g.read(base,2)==b'MZ' and u32(base+u32(base+60)+8)==mods[name]['timestamp']
    while True:
        rel=[e.rva-rva for b in p.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and rva<=e.rva<rva+n]
        end=max([n]+[o+4 for o in rel]);assert end<=64
        if n==end:break
        n=end
    raw=p.get_data(rva,n);assert len(raw)==n;data=bytearray(raw)
    for off in rel:struct.pack_into('<I',data,off,(struct.unpack_from('<I',data,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    actual=g.read(a,n);assert actual==data,(name,hex(rva),'resident mismatch')
    r['runtime_pins'].append(dict(address=hex(a),base=hex(base),rva=hex(rva),module=name,source_sha256=mods[name]['sha256'],raw=raw.hex(),resident=actual.hex(),relocations=rel));return len(r['runtime_pins'])-1
def arm(a):
    if a not in armed:g.bp(a);armed.add(a)
def remove(a):
    if a in armed:g.bp(a,False);armed.remove(a)
def late(a,name):
    index=pin(a);assert a not in sites or sites[a]['name']==name
    sites[a]=dict(name=name,relocated=r['runtime_pins'][index]['resident'],pin=index);arm(a)
def counted(row,label,address,length):
    assert 0<=length<=4096,(label,length)
    row[label]=dict(address=hex(address),length=length,bytes=g.read(address,length).hex() if length else '')
def mapping(pointer,requested):
    assert 0x80000000<=pointer<=0xfffffc00 and pointer%8==0
    assert requested==65536
    pairs=[];raw=b'';total=0
    for i in range(64):
        b=g.read(pointer+i*16,16);length,offset=struct.unpack('<QQ',b);raw+=b
        pairs.append(dict(byte_length=length,volume_byte_offset=offset))
        if length==0:
            assert offset==0 and total==requested
            break
        assert 0<length<=requested-total and offset+length<=oracle['partition_size']
        total+=length
    else:raise AssertionError('Missing terminator within bounded64-pair capture')
    assert pairs==oracle['requested_65536']
    return dict(pointer=hex(pointer),requested_bytes=requested,total_bytes=total,pairs=pairs,raw=raw.hex(),cold_oracle_matched=True)
try:
    command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for a in sites:arm(a)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+600
    for hit in range(256):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in read(launch).get('cycles',[]))
                if returned or time.monotonic()>=deadline:
                    g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_without_final_status' if returned else 'capture_deadline';break
        stopped=True;g.s.settimeout(5)
        if r['status'] in ['dashboard_without_final_status','capture_deadline']:break
        regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
        a=regs['EIP'];assert a in sites,(hex(a),reply);s=sites[a];name=s['name'];assert g.read(a,len(bytes.fromhex(s['relocated']))).hex()==s['relocated']
        row=dict(index=len(r['events']),kind=name,utc=utc(),registers={n:hex(v) for n,v in regs.items()},**who());thread=int(row['thread'],16);r['last_stop']=row
        if name=='configure_entry':
            assert thread not in outer;outer[thread]=dict(stack=regs['ESP'],frame=regs['ESP']-4,handle=hex(u32(regs['ESP']+4)));row['configure']=outer[thread]
            loaded=modules();r['module_list']=loaded;hb=next(v['base'] for v in loaded if v['name'].lower()=='hal.dll')
            row['hal_pins']=[pin(hb+int(v['rva'],16)) for v in review['hal_functions'].values()]
        row['resident_pin']=pin(a)
        if name in ['configure_handle_return','dump_stack_return','complete_call','caller_status','caller_error']:
            cfg=outer[thread];assert regs['EBP']==cfg['frame'];row['status']=hex(regs['EAX']);row['configure_stack']=hex(cfg['stack'])
            if name=='caller_status':
                assert regs['ESP']==cfg['stack']-16
                call=completed[thread];assert regs['ESP']==int(call['stack'],16)+8 and a==int(call['return_address'],16);row['paired_complete_call']=call['index']
                if regs['EAX']<0x80000000:
                    assert regs['EAX']==0 and 'returned_mapping' in r
                    mp=r['returned_mapping'];ctx=u32(K+review['dump_context_global_rva']);assert 0x80000000<=ctx<=0xffffff9f
                    raw=g.read(ctx,0x60);fields=review['dump_context_fields']
                    pointer=struct.unpack_from('<I',raw,fields['mapping_pointer'])[0];n=struct.unpack_from('<I',raw,fields['mapping_bytes'])[0];requested=struct.unpack_from('<Q',raw,fields['requested_bytes'])[0]
                    assert pointer==int(mp['pointer'],16) and requested==mp['requested_bytes']
                    assert n==(len(mp['pairs'])-1)*16+8 and g.read(pointer,n)==bytes.fromhex(mp['raw'])[:n]
                    row['retained_dump_context']=dict(pointer=hex(ctx),raw=raw.hex(),mapping_pointer=hex(pointer),mapping_bytes=n,requested_bytes=requested)
                    row['consumer_pins']=[pin(K+0x22f71,16),pin(K+0x22f8b,25),pin(K+0x22fa4,24)]
                    r['status']='initialization_success_captured'
            if name=='caller_error':
                assert regs['ESP']==cfg['stack']-32 and regs['EAX']>=0x80000000;row['event_id']='0xc0040031';r['status']='failure_path_captured'
        elif name=='stack_entry':
            dump[thread]=dict(stack=regs['ESP'],frame=regs['ESP']-4);row['stack_call']=dump[thread]
        elif name.startswith('stack_'):
            dc=dump[thread];row['status']=hex(regs['EAX'])
            if name=='stack_final_return':assert regs['ESP']==dc['stack']
            else:
                assert regs['EBP']==dc['frame']
                if name=='stack_usage_call':
                    args=struct.unpack('<3I',g.read(regs['ESP'],12));row['arguments']=[hex(v) for v in args];counted(row,'usage_stack',args[1],36)
        elif name=='entry':
            assert thread not in pending;call=dict(index=len(r['calls']),thread=hex(thread),stack=hex(regs['ESP']),frame=hex(regs['ESP']-4),handle=hex(u32(regs['ESP']+4)),return_address=hex(u32(regs['ESP'])))
            pending[thread]=call;r['calls'].append(call);row['call_index']=call['index']
        elif name=='fatx_entry':
            ctx=u32(regs['ESP']+4);irp=u32(ctx);slp=u32(ctx+0x20);sl=g.read(slp,36);code=struct.unpack_from('<I',sl,12)[0]
            assert fsargs and code==fsargs[5] and u32(slp+16)==fsargs[6] and u32(slp+8)==fsargs[7] and u32(slp+4)==fsargs[9]
            call=dict(index=len(r['fatx_calls']),thread=hex(thread),stack=hex(regs['ESP']),return_address=hex(u32(regs['ESP'])),returned=False)
            r['fatx_calls'].append(call);ret=int(call['return_address'],16);returns.setdefault(ret,[]).append(call);late(ret,'fatx_return')
            row.update(fatx_call_index=call['index'],context=hex(ctx),irp=hex(irp),stack_location=sl.hex(),requestor_mode=g.read(irp+field('_IRP','RequestorMode'),1)[0],user_buffer=hex(u32(irp+field('_IRP','UserBuffer'))),io_status=hex(u32(irp+field('_IRP','IoStatus'))))
            counted(row,'input',u32(slp+16),u32(slp+8))
        elif name=='fatx_return':
            matches=[v for v in returns[a] if int(v['thread'],16)==thread and int(v['stack'],16)+4==regs['ESP']];assert len(matches)==1
            call=matches[0];returns[a].remove(call);call.update(returned=True,status=hex(regs['EAX']));row.update(fatx_call_index=call['index'],status=hex(regs['EAX']))
        elif name!='configure_entry':
            call=pending[thread];row['call_index']=call['index'];frame=int(call['frame'],16)
            if name=='return':
                assert regs['ESP']==int(call['stack'],16);call.update(status=hex(regs['EAX']),completed=True);completed[thread]=pending.pop(thread);row['status']=hex(regs['EAX'])
            else:
                assert regs['EBP']==frame
                if name=='handle_return':row.update(status=hex(regs['EAX']),file_object=hex(u32(frame-4)))
                if name in ['query_call','fsctl_call']:
                    args=struct.unpack('<'+'I'*(5 if name=='query_call' else 10),g.read(regs['ESP'],20 if name=='query_call' else 40));row['arguments']=[hex(v) for v in args]
                    if name=='fsctl_call':
                        assert fsargs is None;fsargs=args;counted(row,'input',args[6],args[7]);counted(row,'output_before',args[8],args[9]);counted(row,'iosb_before',args[4],8)
                        fb=next(v['base'] for v in loaded if v['name'].lower()=='xwnfatx.sys');late(fb+review['fatx_entry_rva'],'fatx_entry')
                if name.startswith(('query_','fsctl_')) and not name.endswith('call'):
                    row['status']=hex(u32(frame-0x1c) if 'pending' in name else regs['EAX']);counted(row,'iosb',frame-0x1c,8)
                    if name.startswith('query_'):counted(row,'standard_information',frame-0x34,24)
                    else:
                        assert fsargs;counted(row,'output_after',fsargs[8],fsargs[9]);counted(row,'input_after',fsargs[6],fsargs[7])
                        if row['status']=='0x0':
                            assert 'returned_mapping' not in r
                            r['returned_mapping']=mapping(u32(fsargs[8]),struct.unpack('<Q',g.read(fsargs[6],8))[0]);row['returned_mapping']=r['returned_mapping']
        r['events'].append(row);save()
        if r['status'] in ['failure_path_captured','initialization_success_captured']:break
        remove(a);assert g.ask('s').startswith(('T','S'))
        if name!='fatx_return' or returns[a]:arm(a)
        if time.monotonic()>=deadline:r['status']='capture_deadline';break
    else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc))
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for a in list(armed):remove(a)
            g.send('c');r['guest_resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
        g.s.close()
    elif stopped:command(4594,'cont')
    r.update(ended_utc=utc(),pending_calls=len(pending),unreturned_fatx_calls=sum(not v['returned'] for v in r['fatx_calls']),armed_breakpoints_remaining=[hex(a) for a in armed]);save();lock.close()
print(json.dumps({n:r[n] for n in ['status','error','pending_calls','unreturned_fatx_calls','guest_resumed'] if n in r},indent=2))
