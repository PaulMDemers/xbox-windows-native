"""Bounded debugger observation of input-class port opens; no guest data/code writes."""
import datetime,hashlib,json,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'veto001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(k/'preflight001.json');run=read(out/'run.json')
assert not run['closed'] and not (out/'trace.json').exists()
for name,digest in plan['sources'].items():assert sha(k/name)==digest,name
for path,digest in plan['dependencies'].items():assert sha(Path(path))==digest,path
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
pes={}
for name,p in plan['providers'].items():assert sha(Path(p['path']))==p['sha256'];pes[name]=pefile.PE(p['path'])
K=plan['kernel_base_expected'];L=plan['layouts'];sites={K+rva:name for name,rva in plan['sites'].items()}
sites.update({a:n for n,a in plan['class_sites'].items()});sites.update({a:n for n,a in plan['hid_sites'].items()})
sites.update({K+a:n for n,a in plan['policy_sites'].items()})
static_addresses={K+plan['sites'][n] for n in ('open_enter','open_after_zw','open_end')}|set(plan['class_sites'].values())|set(plan['hid_sites'].values())|{K+a for a in plan['policy_sites'].values()}
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,started_utc=utc(),run_pid=run['pid'],preflight_sha256=sha(k/'preflight001.json'),events=[],open_callers=[],runtime_pins=[],calls=[],hit_counts={},memory_writes=False,register_writes=False)
def save():
    p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def monitor(text):
    with socket.create_connection(('127.0.0.1',4894),timeout=5) as s:
        def reply():
            b=b''
            while not b.endswith(b'(qemu) '):
                part=s.recv(65536)
                if not part:raise EOFError('monitor closed')
                b+=part
            return b.decode(errors='replace')
        reply();s.sendall((text+'\n').encode());return reply()
class Remote:
    def __init__(self):
        self.s=socket.create_connection(('127.0.0.1',4895),timeout=5);self.s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
    def send(self,text):
        b=text.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
    def recv(self):
        while True:
            c=self.s.recv(1)
            if not c:raise EOFError('GDB closed')
            if c not in (b'$',b'%'):continue
            b=bytearray()
            while True:
                c=self.s.recv(1)
                if not c:raise EOFError('GDB packet closed')
                if c==b'#':break
                b+=c
            checksum=b''
            while len(checksum)<2:
                part=self.s.recv(2-len(checksum))
                if not part:raise EOFError('GDB checksum closed')
                checksum+=part
            assert int(checksum,16)==sum(b)%256
            self.s.sendall(b'+')
            if b.startswith(b'O') and len(b)>2 and all(c in b'0123456789abcdefABCDEF' for c in b[1:]):continue
            return b.decode()
    def ask(self,text):self.send(text);return self.recv()
    def read(self,a,n):
        assert 0<n<=4096
        text=self.ask(f'm{a:x},{n:x}');assert not text.startswith('E'),(hex(a),n,text)
        b=bytes.fromhex(text);assert len(b)==n;return b
    def bp(self,a,add=True):assert self.ask(f'{"Z" if add else "z"}0,{a:x},1')=='OK'
g=None;armed=set();stopped=False;loaded=[];verified=set();pending={};share_pending={};serial=0
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def field(t,n):return L[t]['fields'][n]['offset']
def uni(a):
    n,maximum,p=struct.unpack('<HHI',g.read(a,8));assert n<=maximum and n<=1024 and n%2==0
    return g.read(p,n).decode('utf-16le') if n else ''
def who():
    t=u32(0xffdff124);p=u32(t+plan['thread_owner_offset'])
    return dict(thread=t,process=p,pid=u32(p+field('_EPROCESS','UniqueProcessId')),image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'))
def modules():
    head=K+plan['module_list_rva'];q=u32(head);rows=[];seen=set()
    while q!=head:
        assert q and q not in seen and len(seen)<160;seen.add(q);node=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
        rows.append(dict(base=u32(node+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(node+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(node+field('_LDR_DATA_TABLE_ENTRY','BaseDllName')).lower()));q=u32(q)
    return rows
def locate(a):
    global loaded
    match=next((x for x in loaded if x['base']<=a<x['base']+x['size']),None)
    if match is None:loaded=modules();match=next((x for x in loaded if x['base']<=a<x['base']+x['size']),None)
    return dict(address=a,module=match['name'],base=match['base'],rva=a-match['base']) if match else dict(address=a,module=None)
def pin(a):
    global loaded
    if a in verified:return
    if not K<=a<K+plan['providers']['ntoskrnl.exe']['image_size']:loaded=modules()
    m=locate(a);name=m['module'];assert name in pes,(hex(a),m)
    pe=pes[name];base=m['base'];rva=m['rva']
    if a in plan['class_sites'].values():
        expected={'kbd_enable_enter':('kbdclass.sys',0xf46),'kbd_enable_end':('kbdclass.sys',0x110d),'mou_enable_enter':('mouclass.sys',0xe6e),'mou_enable_end':('mouclass.sys',0xfcf)}[sites[a]]
        assert (name,rva)==expected,(m,expected)
    if a in plan['hid_sites'].values():assert name=='hidclass.sys' and rva==a-0xf8f10000,(m,sites[a])
    assert g.read(base,2)==b'MZ'
    nt=u32(base+60);assert u32(base+nt+8)==pe.FILE_HEADER.TimeDateStamp and u32(base+nt+0x50)==pe.OPTIONAL_HEADER.SizeOfImage
    n=16
    while True:
        rel=[e.rva-rva for b in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and rva<=e.rva<rva+n]
        end=max([n]+[v+4 for v in rel]);assert end<=32
        if end==n:break
        n=end
    raw=pe.get_data(rva,n);expected=bytearray(raw)
    for v in rel:struct.pack_into('<I',expected,v,(struct.unpack_from('<I',expected,v)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    actual=g.read(a,n);assert actual==expected,(name,hex(rva),'resident site mismatch')
    r['runtime_pins'].append(dict(**m,provider_sha256=plan['providers'][name]['sha256'],raw=raw.hex(),resident=actual.hex(),relocations=rel));verified.add(a)
def device(a):
    if not a:return None
    b=g.read(a,L['_DEVICE_OBJECT']['size']);typ,size=struct.unpack_from('<HH',b);assert typ==3 and size>=L['_DEVICE_OBJECT']['size']
    row=dict(address=a,type=typ,size=size)
    for n in ('ReferenceCount','DriverObject','AttachedDevice','Flags','DeviceExtension','DeviceType'):row[n]=struct.unpack_from('<I',b,field('_DEVICE_OBJECT',n))[0]
    d=row['DriverObject'];assert struct.unpack('<H',g.read(d,2))[0]==4
    row.update(driver_name=uni(d+field('_DRIVER_OBJECT','DriverName')),driver_start=u32(d+field('_DRIVER_OBJECT','DriverStart')),create_dispatch=locate(u32(d+field('_DRIVER_OBJECT','MajorFunction'))))
    return row
def file_info(a):
    if not a:return None
    b=g.read(a,L['_FILE_OBJECT']['size']);typ,size=struct.unpack_from('<HH',b);assert typ==5 and size>=L['_FILE_OBJECT']['size']
    row=dict(address=a,type=typ,size=size)
    for n in ('DeviceObject','FsContext','FsContext2','RelatedFileObject','Flags'):row[n]=struct.unpack_from('<I',b,field('_FILE_OBJECT',n))[0]
    for n in ('ReadAccess','WriteAccess','DeleteAccess','SharedRead','SharedWrite','SharedDelete'):row[n]=b[field('_FILE_OBJECT',n)]
    row['FileName']=uni(a+field('_FILE_OBJECT','FileName'));return row
def optional(fn,*args):
    try:return fn(*args)
    except Exception as e:return dict(read_error=repr(e))
def share(a):return dict(zip(('OpenCount','Readers','Writers','Deleters','SharedRead','SharedWrite','SharedDelete'),struct.unpack('<7I',g.read(a,28))))
def arm(a):
    if a not in armed:g.bp(a);armed.add(a)
def unarm(a):
    if a in armed:g.bp(a,False);armed.remove(a)
def extras(enable):
    for name in ('share_enter','share_failure','share_end','call_driver'):
        a=K+plan['sites'][name]
        if enable:arm(a)
        else:unarm(a)
exec(compile((k/'policy-observe.py').read_text(),str(k/'policy-observe.py'),'exec'))
exec(compile((k/'stack-observe.py').read_text(),str(k/'stack-observe.py'),'exec'))
exec(compile((k/'hid-observe.py').read_text(),str(k/'hid-observe.py'),'exec'))
try:
    monitor('stop');stopped=True;g=Remote();r['gdb_features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for address in static_addresses:arm(address)
    r['status']='armed_before_launch';save();g.send('c');stopped=False;(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+240
    for hit in range(4096):
        g.s.settimeout(max(.1,min(5,deadline-time.monotonic())))
        try:reply=g.recv();stopped=True
        except socket.timeout:
            if time.monotonic()<deadline:continue
            r['status']='capture_deadline';break
        regs=dict(zip(('eax','ecx','edx','ebx','esp','ebp','esi','edi','eip','eflags'),struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])))
        a=regs['eip'];assert a in sites,(reply,regs)
        label=sites[a];r['hit_counts'][label]=r['hit_counts'].get(label,0)+1;pin(a);identity=who();thread=identity['thread']
        if label.startswith('policy_'):
            policy_observation(label,regs,identity)
        elif label.endswith('_enable_enter'):
            args=struct.unpack('<5I',g.read(regs['esp'],20));serial+=1;extension=args[3]
            call=dict(id=serial,kind='class_enable',entry_utc=utc(),entry_esp=regs['esp'],identity=identity,caller=locate(a),name=label.split('_')[0]+':'+hex(extension),enable=args[1]&255,irp=args[2],extension=extension,file_output=args[4],before_file_output=optional(u32,args[4]),extension_prefix=optional(lambda a:g.read(a,48).hex(),extension),class_device=optional(lambda a:device(u32(a)),extension),lower_device=optional(lambda a:device(u32(a+8)),extension),file_before=optional(lambda a:file_info(u32(a)),args[4]),steps=[])
            call['entry_stack']=optional(stack_observation,regs,True)
            call['entry_registers']=regs
            call['raw_entry_args']=list(args)
            r['calls'].append(call);pending.setdefault(thread,[]).append(call);extras(True)
        elif label=='open_enter':
            args=struct.unpack('<5I',g.read(regs['esp'],20))
            # Driver ranges can be reused after unload; refresh before classifying any external caller.
            if not K<=args[0]<K+plan['providers']['ntoskrnl.exe']['image_size']:loaded=modules()
            caller=locate(args[0]);r['open_callers'].append(dict(utc=utc(),entry_esp=regs['esp'],raw_args=list(args),caller=caller))
            if caller['module'] in ('kbdclass.sys','mouclass.sys'):
                pin(args[0]);serial+=1
                call=dict(id=serial,kind='object_pointer_open',entry_utc=utc(),entry_esp=regs['esp'],identity=identity,caller=caller,name=uni(args[1]),desired_access=args[2],file_output=args[3],device_output=args[4],before_file_output=optional(u32,args[3]),steps=[])
                call['caller_frame_words']=optional(lambda p:list(struct.unpack('<4I',g.read(p+8,16))),regs['ebp'])
                call['prior_same_name']=[dict(id=x['id'],status=x.get('status'),file_output=x['file_output'],current_slot=optional(u32,x['file_output']),returned_file=x.get('returned_file'),file_now=optional(file_info,x['returned_file']['address']) if isinstance(x.get('returned_file'),dict) and 'address' in x['returned_file'] else None) for x in r['calls'] if x['name']==call['name'] and x.get('status')==0]
                call['entry_stack']=optional(stack_observation,regs,True)
                call['entry_registers']=regs
                call['raw_entry_args']=list(args)
                r['calls'].append(call);pending.setdefault(thread,[]).append(call);extras(True)
        elif pending.get(thread):
            call=pending[thread][-1];entry=dict(site=label,utc=utc(),identity=identity,call_id=call['id'],registers=regs)
            if label.startswith('hid_'):
                entry.update(hid_observation=hid_observation(regs,label))
                if label=='hid_sharing_status':entry['rejection_stack']=optional(stack_observation,regs,False)
            elif label.endswith('_enable_end'):
                assert call['kind']=='class_enable' and regs['ebp']+4==call['entry_esp'];call['status']=regs['esi'];call['end_utc']=utc();call['file_after']=optional(lambda a:file_info(u32(a)),call['file_output']);call['irp_status_at_end']=optional(u32,call['irp']+field('_IRP','IoStatus'))
                pending[thread].pop()
                if not any(pending.values()):extras(False)
            elif label in ('open_after_zw','open_end') and (call['kind']!='object_pointer_open' or regs['ebp']+4!=call['entry_esp']):
                entry=None
            elif label=='open_after_zw':
                assert regs['ebp']+4==call['entry_esp'];entry['zw_open_status']=regs['eax'];call['zw_open_status']=regs['eax']
            elif label=='open_end':
                assert regs['ebp']+4==call['entry_esp'];call['status']=regs['edi'];call['end_utc']=utc()
                if regs['edi']<0x80000000:
                    call['returned_file']=optional(file_info,u32(call['file_output']));call['returned_device']=optional(device,u32(call['device_output']))
                else:call['after_failure_output_slot']=optional(u32,call['file_output'])
                pending[thread].pop()
                if not any(pending.values()):extras(False)
            elif label=='call_driver':
                irp=regs['edx'];stack=u32(irp+0x60)-L['_IO_STACK_LOCATION']['size'];b=g.read(stack,L['_IO_STACK_LOCATION']['size'])
                if b[0]==0:
                    entry.update(irp=irp,major=0,minor=b[1],stack_bytes=b.hex(),target=optional(device,regs['ecx']),file=optional(file_info,struct.unpack_from('<I',b,field('_IO_STACK_LOCATION','FileObject'))[0]))
                else:entry=None
            elif label=='share_enter':
                args=struct.unpack('<6I',g.read(regs['esp'],24));entry.update(caller=locate(args[0]),desired_access=args[1],desired_share=args[2],file=optional(file_info,args[3]),share_address=args[4],share_before=optional(share,args[4]),update=args[5]&255)
                share_pending[(thread,regs['esp'])]=dict(file=args[3],share=args[4],event=entry)
            elif label in ('share_failure','share_end'):
                state=share_pending.get((thread,regs['ebp']+4))
                if state:entry.update(share_address=state['share'],share_current=optional(share,state['share']),file=optional(file_info,state['file']),status=0xc0000043 if label=='share_failure' else regs['eax'])
                else:entry['unmatched_share_frame']=True
                if label=='share_end':share_pending.pop((thread,regs['ebp']+4),None)
            if entry:call['steps'].append(entry);r['events'].append(entry)
        save()
        failed={c['caller']['module'] for c in r['calls'] if c.get('status')==0xc0000043}
        if failed=={'kbdclass.sys','mouclass.sys'} and not any(pending.values()) and policy_finished():r['status']='both_class_failures_captured';break
        if time.monotonic()>=deadline:r['status']='capture_deadline';break
        unarm(a);assert g.ask('s').startswith(('T','S'))
        if a in static_addresses or any(pending.values()):arm(a)
        g.send('c');stopped=False
    else:r['status']='stop_count_bound'
except Exception as e:
    r.update(status='capture_incomplete',error=repr(e),traceback=traceback.format_exc())
finally:
    if g:
        try:
            g.s.settimeout(5)
            if not stopped:g.s.sendall(b'\x03');g.recv();stopped=True
            for a in list(armed):unarm(a)
            g.send('c');stopped=False;r['guest_resumed']=True;r['breakpoints_remaining']=len(armed)
        except Exception as e:
            r['cleanup_error']=repr(e)
            try:monitor('cont');r['monitor_resumed']=True
            except Exception as inner:r['monitor_resume_error']=repr(inner)
        g.s.close()
    r['finished_utc']=utc();r['pending_call_count']=sum(map(len,pending.values()));save()
print(json.dumps({x:r.get(x) for x in ('status','error','hit_counts','guest_resumed','cleanup_error','pending_call_count')}))
