"""Observe one intentional guest crash and dump return; never inject execution."""
import datetime,hashlib,json,socket,struct,sys,time,re
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001';run=ws/'work/runs/nt5-video-shared-crash-crash001'
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
g=None;stopped=False;armed=set();loaded=[];entry=None;ret=None;nv_shutdown=None;nv_idle=None;nv_return=None;nv_entry=None;atapi_base=None;atapi_sites={};writer_pair=None;write_entry=None;write_returns={};write_count=0;write_bytes=0;lock=acquire_monitor_lock(4594)
render_sites={};video=read(k/'video-sites.json')['modules']['bootvid.dll'];bootbase=None
def video_state():
    return dict(globals={n:u32(bootbase+video['symbols'][n]) for n in ['_FrameBufferStart','_BackBuffer','_Owner','_References','_Ready']},published=list(struct.unpack('<11I',g.read(bootbase+video['symbols']['_Published'],44))))

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
    m=next(v for v in loaded if v['base']<=a<v['base']+v['size']);name=m['name'].lower();base=m['base'];rva=a-base
    if name not in pes:
        assert g.read(base,2)==b'MZ';peoff=u32(base+60)
        assert 0x40<=peoff<4096 and g.read(base+peoff,4)==b'PE\0\0'
        stamp=u32(base+peoff+8);size=u32(base+peoff+0x50)
        matches=[n for n,v in mods.items() if v['timestamp']==stamp and v['image_size']==size]
        assert len(matches)==1,('Unpinned loaded module identity',m,matches)
        name=matches[0]
    p=pes[name]
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
    r['runtime_pins'].append(dict(address=hex(a),base=hex(base),rva=hex(rva),module=name,loaded_name=m['name'],source_sha256=mods[name]['sha256'],raw=raw.hex(),resident=actual.hex(),relocations=rel));return len(r['runtime_pins'])-1

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
            if not 0x40<=peoff<4096 or g.read(base+peoff,4)!=b'PE\0\0':continue
            ts=u32(base+peoff+8);size=u32(base+peoff+0x50)
            matches=[n for n,m in mods.items() if m['timestamp']==ts and m['image_size']==size]
            if len(matches)!=1:continue
            loaded.append(dict(base=base,size=(size+4095)&~4095,name=matches[0],discovery='bounded callback PE scan'))
            r['module_list']=loaded;break
        else:raise AssertionError('Cannot pin actual dump callback within bounded128 pages')
    return pin(a)
bc=K+kr['sites']['_KeBugCheckEx@20'];dump=K+kr['sites']['_IoWriteCrashDump@24'];initret=K+0x21ed4;precall=K+0x2b141;writecall=K+0x22100;writeret=K+0x22103
stages={K+rva:label for rva,label in [(0x2b079,'stop_line_call'),(0x2b082,'message_call'),(0x2b087,'message_return'),(0x2b0d0,'callbacks_call'),(0x2b0d5,'callbacks_return'),(0x2b0ed,'driver_name_call'),(0x2b0f2,'driver_name_done'),(0x2b106,'debugger_init_call'),(0x2b10b,'debugger_init_return'),(0x2b117,'context_copy')]}
try:
    command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for a in [bc,dump,initret,precall,writecall]+list(stages):arm(a)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+600
    for hit in range(64):
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
            bootbase=next(v['base'] for v in loaded if v['name'].lower()=='bootvid.dll');r['boot_before']=video_state()
            for name in ['VidResetDisplay','VidDisplayString','VidSolidColorFill','VidBufferToScreenBlt']:
                addr=bootbase+video['exports'][name];render_sites[addr]=name;arm(addr)
            row['kind']='bugcheck_entry';row['arguments']=[hex(v) for v in struct.unpack('<5I',g.read(regs['ESP']+4,20))]
            row['caller']=hex(u32(regs['ESP']));row['caller_pin']=pin(u32(regs['ESP']))
            assert row['arguments']==['0xe058d103','0x44554d50','0x103','0x10000','0x1'],'Unexpected bugcheck'
            row['resident_dispatch_pins']={n:pin(next(v['base'] for v in loaded if v['name'].lower()==n)+rva) for n,rva in [('hal.dll',0x8290),('xwnfatx.sys',int(read(k/'fatx-review.json')['candidate001']['resident_functions']['_VfatFileSystemControl']['rva'],16))]}
            row['dump_context']=dump_context();remove(bc)
            nvbase=next(v['base'] for v in loaded if v['name'].lower()=='nvnetnt5.sys');sites=read(k/'nvnet-review.json')['candidate001']['functions']
            nv_shutdown=nvbase+int(sites['_MiniportShutdown@4']['rva'],16);nv_idle=nvbase+int(sites['_NvNetIdleTransmitter']['rva'],16)
            row['nvnet_pins']=[pin(nv_shutdown),pin(nv_idle)];arm(nv_shutdown);arm(nv_idle)
        elif a in render_sites:
            row['kind']='bootvid_render_entry';row['function']=render_sites[a];row['state']=video_state();row['irql']=g.read(0xffdff024,1).hex();remove(a)
        elif a==nv_shutdown:
            row['kind']='nvnet_shutdown_entry';nv_entry=dict(stack=regs['ESP'],thread=row['thread']);nv_return=u32(regs['ESP']);row['adapter']=hex(u32(regs['ESP']+4));row['caller_pin']=pin(nv_return);arm(nv_return);remove(a)
        elif a==nv_idle:
            row['kind']='nvnet_idle_entry';row['arguments']=[hex(v) for v in struct.unpack('<2I',g.read(regs['ESP']+4,8))];remove(a)
        elif a==nv_return:
            row['kind']='nvnet_shutdown_return';assert row['thread']==nv_entry['thread'] and regs['ESP']==nv_entry['stack']+8;remove(a)
        elif a in stages:
            row['kind']=stages[a];row['stack32']=g.read(regs['ESP'],32).hex();remove(a)
        elif a==precall:
            row['kind']='pre_dump_call';row['context']=dump_context();remove(a)
        elif a==dump:
            row['kind']='dump_entry';remove(a);assert entry is None and r['events'][0]['kind']=='bugcheck_entry'
            row['arguments']=[hex(v) for v in struct.unpack('<6I',g.read(regs['ESP']+4,24))]
            assert row['arguments'][:5]==r['events'][0]['arguments']
            entry=dict(stack=regs['ESP'],thread=row['thread'],return_address=u32(regs['ESP']));ret=entry['return_address'];row['pair']=entry;row['context']=dump_context();arm(ret)
        elif a==initret:
            row['kind']='dump_stack_initialized';remove(a);assert entry is not None
            row['status']=hex(regs['EAX']);row['context']=dump_context()
            if regs['EAX']<0x80000000:
                raw=bytes.fromhex(row['context']['stack_raw']);callbacks=[struct.unpack_from('<I',raw,v)[0] for v in [0x30,0x34]]
                row['callbacks']=[dict(address=hex(v),pin=callback_pin(v)) for v in callbacks]
                write_entry=callbacks[0];arm(write_entry)
        elif a==writecall:
            row['kind']='first_write_call';offset_ptr=u32(regs['ESP']);mdl=u32(regs['ESP']+4);raw=g.read(mdl,28)
            row['volume_offset']=struct.unpack('<Q',g.read(offset_ptr,8))[0];row['mdl_raw']=raw.hex();mapped,start,count,offset=struct.unpack_from('<4I',raw,12);row['byte_count']=count;row['source_prefix']=g.read(mapped,64).hex();row['writer']=hex(u32(regs['EBP']-0x18));row['writer_pin']=callback_pin(u32(regs['EBP']-0x18));remove(a)
            atapi_base=int(row['writer'],16)-0x13454;assert r['runtime_pins'][row['writer_pin']]['module']=='atapi.sys' and r['runtime_pins'][row['writer_pin']]['rva']=='0x13454'
            writer_pair=dict(thread=row['thread'],stack=regs['ESP']);atapi_sites={atapi_base+v:n for n,v in read(k/'address-review.json')['sites'].items()}
            row['internal_pins']={name:pin(site) for site,name in atapi_sites.items()}
            for site in atapi_sites:arm(site)
        elif a==write_entry:
            row['kind']='write_payload_entry';row['write_index']=write_count
            offset_ptr,mdl=struct.unpack('<2I',g.read(regs['ESP']+4,8));row['volume_offset']=struct.unpack('<Q',g.read(offset_ptr,8))[0]
            raw=g.read(mdl,28);mapped,start,count,offset=struct.unpack_from('<4I',raw,12)
            assert 0<count<=131072 and write_bytes+count<=65536 and write_count<16
            payload=b''.join(g.read(mapped+i,min(2048,count-i)) for i in range(0,count,2048))
            artifact=out/'artifacts'/('write-payload-%02d.bin'%write_count);assert not artifact.exists();artifact.write_bytes(payload)
            row.update(mdl_raw=raw.hex(),byte_count=count,payload_sha256=hashlib.sha256(payload).hexdigest(),payload_file=artifact.name)
            retaddr=u32(regs['ESP']);row['return_pin']=callback_pin(retaddr);assert retaddr not in write_returns
            write_returns[retaddr]=dict(stack=regs['ESP'],thread=row['thread'],write_index=write_count);write_count+=1;write_bytes+=count;arm(retaddr);remove(a)
        elif a in write_returns:
            pair=write_returns.pop(a);row['kind']='write_payload_return';row['write_index']=pair['write_index'];row['status']=hex(regs['EAX'])
            assert row['thread']==pair['thread'] and regs['ESP']==pair['stack']+12;remove(a);arm(write_entry)
        elif a in atapi_sites:
            row['kind']=atapi_sites[a];assert row['thread']==writer_pair['thread'];row['writer_pair']=writer_pair
            if row['kind']=='divide_call':
                low,high,divlow,divhigh=struct.unpack('<4I',g.read(regs['ESP'],16));row['dividend']=low+(high<<32);row['divisor']=divlow+(divhigh<<32)
                row['partition_offset']=struct.unpack('<Q',g.read(atapi_base+0xc468,8))[0];row['sector_size']=u32(atapi_base+0xc464)
            elif row['kind']=='divide_return':row['quotient']=regs['EAX']+(regs['EDX']<<32)
            elif row['kind']=='dispatch_call':
                adapter,srb=struct.unpack('<2I',g.read(regs['ESP'],8));row['adapter']=hex(adapter);row['srb']=hex(srb);row['srb_raw']=g.read(srb,64).hex();row['cdb_lba']=int.from_bytes(g.read(srb+0x32,4),'big');row['cdb_count']=int.from_bytes(g.read(srb+0x37,2),'big');target_id=g.read(srb+6,1)[0];row['device_flags']=u32(adapter+target_id*4+0xb0);row['command_table']=g.read(adapter+target_id*0x3c+0x90c,5).hex()
            elif row['kind']=='decoded_lba':row['lba']=regs['EBX'];row['device_flags']=u32(regs['ESI']+(g.read(regs['EDI']+6,1)[0]*4)+0xb0)
            elif row['kind'] in ['before_head_mask','after_head_mask']:row['al']=regs['EAX']&255;row['lba']=regs['EBX']
            elif row['kind']=='select_write_command':row['command']=g.read(regs['EAX']+regs['ESI']+0x90d,1)[0];row['adapter']=hex(regs['ESI'])
            elif row['kind']=='write_command_call':row['port'],row['command_argument']=struct.unpack('<2I',g.read(regs['ESP'],8))
            elif row['kind']=='selector_entry':
                row['full_selector_pins']=[pin(a,64),pin(a+64,41)]
                adapter,srb=struct.unpack('<2I',g.read(regs['ESP']+4,8));target=g.read(srb+6,1)[0];row['flags']=u32(adapter+target*4+0xb0);row['extended_command']=g.read(adapter+target*0x3c+0x910,1)[0]
            elif row['kind']=='extended_entry':row['arguments']=[hex(v) for v in struct.unpack('<2I',g.read(regs['ESP']+4,8))]
            elif row['kind']=='extended_decoded_lba':row['lba']=regs['ECX']
            elif row['kind']=='extended_high_byte':row['al']=regs['EAX']&255
            elif row['kind']=='extended_command_call':row['port'],row['command_argument']=struct.unpack('<2I',g.read(regs['ESP'],8))
            remove(a)
        elif a==writeret:
            row['kind']='first_write_return';assert row['thread']==writer_pair['thread'] and regs['ESP']==writer_pair['stack']+8;row['status']=hex(regs['EAX']);remove(a)
        elif a==ret:
            row['kind']='dump_return';assert row['thread']==entry['thread'] and regs['ESP']==entry['stack']+28
            row['eax']=hex(regs['EAX']);row['returned_boolean']=regs['EAX']&255;row['final_status']=hex(u32(K+kr['sites']['_IopFinalCrashDumpStatus']));row['context']=dump_context()
            r['boot_after']=video_state()
            text=command(4594,'info registers');r['control_registers']={n:int(re.search(n+r'=([0-9a-fA-F]+)',text).group(1),16) for n in ['CR0','CR3','CR4']}
            raw=out/'artifacts/crash-return.ram';assert not raw.exists();command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()));assert raw.stat().st_size==67108864
            r['private_memory']=str(raw.resolve());r['private_memory_sha256']=sha(raw)
            r['status']='dump_return_observed';save();break
        save()
    else:r['status']='hit_limit'
except BaseException as exc:
    import traceback
    r['host_traceback']=traceback.format_exc()
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
