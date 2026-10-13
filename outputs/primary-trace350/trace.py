"""One operation per large direction; read-only calls, bounded trace, full teardown."""
import datetime,hashlib,json,re,socket,struct,sys,time,traceback
from pathlib import Path
from protocol import surface as decode_surface,paired
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'candidate001';run=Path('E:/xwn350/runs/nt5-primary350-candidate001')
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sys.path.insert(0,str(K.parent/'surface-bridge260'));from atomic_json import write_json
sys.path.insert(0,str(K.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(K.parent/'video-cursor-scanout'));from discover_kernel import discover
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
plan=read(K/'sites002.json');pes={}
for name,h in read(out/'emulator-frozen.json').items():assert sha(W/name)==h,name
for name,m in plan['modules'].items():assert sha(Path(m['path']))==m['sha256'];pes[name]=pefile.PE(m['path'])
L=read(K.parent/'video-row-copy-trace/layouts.json')['structures'];pubs=read(K.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols']
code=(K.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(debugger=True,physical_access=False,ordinary_qualified=False,performance_qualified=False,guest_memory_writes=False,guest_register_writes=False,started_utc=utc(),events=[],operations=[],pins=[],headers={},other_hits=[],status='initializing')
g=None;lock=None;stopped=False;armed=set();loaded=[];addresses={};pending=[];active=None;selected=None;completed=[];kernel=None
def save():write_json(out/'trace.json',r)
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def words(a,n):return list(struct.unpack('<'+'I'*n,g.read(a,n*4)))
def field(t,n):return L[t]['fields'][n]['offset']
def who():
    t=u32(0xffdff124);p=u32(t+plan['thread_owner_offset'])
    return dict(thread=t,process=p,image=g.read(p+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0].decode('ascii',errors='replace'),base=u32(p+field('_EPROCESS','SectionBaseAddress')))
def uni(a):
    n,m,p=struct.unpack('<HHI',g.read(a,8));assert n%2==0 and n<=m<=2048
    return g.read(p,n).decode('utf-16le') if n else ''
def modules(process):
    head=kernel+plan['module_list_rva'];q=u32(head);last=head;seen=set();rows=[]
    while q!=head:
        assert q and q not in seen and len(seen)<200;seen.add(q);assert u32(q+4)==last
        n=q-field('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
        rows.append(dict(base=u32(n+field('_LDR_DATA_TABLE_ENTRY','DllBase')),size=u32(n+field('_LDR_DATA_TABLE_ENTRY','SizeOfImage')),name=uni(n+field('_LDR_DATA_TABLE_ENTRY','BaseDllName')).lower()));last=q;q=u32(q)
    assert u32(head+4)==last
    peb=u32(process+field('_EPROCESS','Peb'));ldr=u32(peb+12);head=ldr+12;q=u32(head);last=head;seen=set()
    while q!=head:
        assert q and q not in seen and len(seen)<100;seen.add(q);assert u32(q+4)==last
        rows.append(dict(base=u32(q+24),size=u32(q+32),name=uni(q+44).lower()));last=q;q=u32(q)
    assert u32(head+4)==last
    return rows
def pin(name,rva,n=32):
    m=next(v for v in loaded if v['name']==name);p=pes[name];base=m['base']
    assert m['size']==((p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
    if name not in r['headers']:
        try:
            assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096 and g.read(base+nt,4)==b'PE\0\0'
            assert u32(base+nt+8)==p.FILE_HEADER.TimeDateStamp
            r['headers'][name]=dict(readable=True,base=base,timestamp=p.FILE_HEADER.TimeDateStamp)
        except AssertionError as e:
            if str(e)!='E14' or name=='ntoskrnl.exe':raise
            r['headers'][name]=dict(readable=False,error='E14',base=base,identity='Loader name/base/size plus exact relocated resident code; cold full binary hash. No header residency claim.')
    while True:
        rel=[e.rva-rva for b in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in b.entries if e.type==3 and rva<=e.rva<rva+n]
        size=max([n]+[v+4 for v in rel]);assert size<=4096
        if n==size:break
        n=size
    raw=p.get_data(rva,n);assert len(raw)==n;expected=bytearray(raw)
    for v in rel:struct.pack_into('<I',expected,v,(struct.unpack_from('<I',expected,v)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    actual=g.read(base+rva,n);assert actual==expected,(name,hex(rva),'resident mismatch')
    r['pins'].append(dict(module=name,base=base,rva=rva,raw=raw.hex(),resident=actual.hex(),relocations=rel,source_sha256=plan['modules'][name]['sha256']));return len(r['pins'])-1
def pin_address(a):
    matches=[m for m in loaded if m['name'] in pes and m['base']<=a<m['base']+m['size']];assert len(matches)==1
    m=matches[0];return pin(m['name'],a-m['base'])
def arm(a):
    if a not in armed:g.bp(a);armed.add(a)
def remove(a):
    if a in armed:g.bp(a,False);armed.remove(a)
def surface(a):
    return decode_surface(g.read(a,52),a)
def clip(a):
    if not a:return None
    raw=g.read(a,24);return dict(address=a,raw=raw.hex(),bounds=list(struct.unpack_from('<4i',raw,4)),complexity=raw[20])
def record_call(label,regs,owner,args):
    assert len(pending)<8 and len(active['calls'])<128
    call=dict(index=len(active['calls']),label=label,thread=owner['thread'],process=owner['process'],stack=regs['ESP'],caller_ebp=regs['EBP'],return_address=u32(regs['ESP']),arguments=args,returned=False,entry_pin=pin_address(regs['EIP']))
    call['expected_return_sp']=regs['ESP']+4+(24 if label=='copy' else 0)
    call['return_pin']=pin_address(call['return_address'])
    if label=='primary':
        p,d,s,c,x,rect,point,b=args
        call.update(pdev=p,destination=surface(d),source=surface(s),clip=clip(c),xlate=None if not x else dict(address=x,raw=g.read(x,20).hex(),flags=u32(x+4)),rect=list(struct.unpack('<4i',g.read(rect,16))),source_origin=list(struct.unpack('<2i',g.read(point,8))),bytes_pointer=b,pdev_prefix=g.read(p,0x1a4).hex(),owner_results=[])
    pending.append(call);active['calls'].append(call);arm(call['return_address']);return call
try:
    lock=acquire_monitor_lock(5186);command(5186,'stop');stopped=True;g=Remote(5187);g.s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
    r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?');assert g.ask('Qqemu.PhyMemMode:0')=='OK';assert g.ask('qqemu.PhyMemMode')=='0'
    realread=g.read
    def checked_read(a,n):
        assert 0<n<=4096 and 0<=a<=0xffffffff and a+n<=0x100000000
        try:return realread(a,n)
        except Exception:
            r.setdefault('read_errors',[]).append(dict(address=a,bytes=n,stack=traceback.format_stack(limit=5)));save();raise
    g.read=checked_read
    marker=plan['modules']['replay.exe']['preferred_base']+plan['sites']['interval']['rva'];arm(marker)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+600
    for hit in range(512):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                if time.monotonic()>deadline:raise TimeoutError('600-second diagnostic bound')
        stopped=True;g.s.settimeout(5);assert time.monotonic()<deadline
        regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
        a=regs['EIP'];assert a in armed,(hex(a),reply);owner=who();r['last_registers']=regs
        if owner['image'].lower()!='replay.exe' or (selected and owner['process']!=selected['process']) or (active and owner['thread']!=active['thread']):
            r['other_hits'].append(dict(registers=regs,owner=owner));assert len(r['other_hits'])<=32
        elif a==marker:
            assert active is None and not pending
            id=u32(regs['EBP']-0x4c0);kind=u32(regs['EBP']-0x4c4);assert id<15 and kind==id%5
            if id in [12,13] and id not in completed:
                assert id==12+len(completed);assert owner['base']==plan['modules']['replay.exe']['preferred_base']
                if not loaded:
                    kernel,discovery=discover(g.read,command(5186,'info registers'),pes['ntoskrnl.exe'],pubs);r['kernel_discovery']=discovery
                    loaded=modules(owner['process']);r['loaded_modules']=loaded
                    for gate in discovery['gates']:pin('ntoskrnl.exe',gate['rva'])
                    for label,site in plan['sites'].items():
                        m=next(v for v in loaded if v['name']==site['module']);addresses[label]=m['base']+site['rva'];pin(site['module'],site['rva'])
                    assert addresses['interval']==marker
                    # Entire new helper resident code through the next function.
                    pin('xwnown.dll',0x4550,0x620)
                    pin('replay.exe',0x5258,0x286)
                selected=dict(id=id,thread=owner['thread'],process=owner['process'],frame=regs['EBP'],marker_pin=pin_address(a))
                arm(addresses['operation'])
            r['events'].append(dict(kind='interval',id=id,owner=owner,registers=regs))
        elif a==addresses.get('operation'):
            assert selected and active is None and owner['thread']==selected['thread'] and regs['EBP']==selected['frame']
            args=words(regs['ESP'],9);assert args[0]==args[5] and args[3:5]==[960,540] and args[8]==0xcc0020
            assert args[1:3]==([32,32] if selected['id']==12 else [16,16]);assert args[6:8]==([16,16] if selected['id']==12 else [32,32])
            active=dict(**selected,arguments=args,calls=[],events=[],start_utc=utc(),stack=regs['ESP'],bitblt_returned=False)
            target=u32(owner['base']+0x9144);api=next(e.address for e in pes['gdi32.dll'].DIRECTORY_ENTRY_EXPORT.symbols if e.name==b'BitBlt')
            assert target==next(m['base'] for m in loaded if m['name']=='gdi32.dll')+api
            active['bitblt_target_pin']=pin('gdi32.dll',api)
            r['operations'].append(active);remove(a)
            for label in ['copy','primary','owner_dst_return','owner_src_return','bitblt_return','flush_return']:arm(addresses[label])
        elif active:
            matches=[c for c in pending if paired(c,a,regs['ESP'],owner['thread'],owner['process'])]
            if matches:
                assert len(matches)==1 and pending[-1] is matches[0];call=pending.pop();call.update(returned=True,result=regs['EAX'],returned_utc=utc())
                if call['label']=='primary':call['copied_bytes']=struct.unpack('<Q',g.read(call['bytes_pointer'],8))[0]
                if a not in addresses.values() and not any(c['return_address']==a for c in pending):remove(a)
                active['events'].append(dict(kind='return',call=call['index'],registers=regs))
            elif a in [addresses['owner_dst_return'],addresses['owner_src_return']]:
                assert pending and pending[-1]['label']=='primary';call=pending[-1];assert regs['EBP']==call['stack']-4
                call['owner_results'].append(dict(side='destination' if a==addresses['owner_dst_return'] else 'source',value=regs['EAX'],pin=pin_address(a)))
            elif a in [addresses['copy'],addresses['primary']]:
                label='copy' if a==addresses['copy'] else 'primary';call=record_call(label,regs,owner,words(regs['ESP']+4,6 if label=='copy' else 8))
                if label=='primary':assert len(pending)>=2 and pending[-2]['label']=='copy'
                active['events'].append(dict(kind='entry',call=call['index'],registers=regs))
            elif a==addresses['bitblt_return']:
                assert not pending and regs['ESP']==active['stack']+36 and regs['EAX']!=0 and regs['EBP']==active['frame'];active['bitblt_returned']=True;remove(a)
            elif a==addresses['flush_return']:
                assert active['bitblt_returned'] and not pending and regs['EAX']!=0 and regs['EBP']==active['frame']
                active.update(complete=True,end_utc=utc(),flush_pin=pin_address(a));completed.append(active['id']);active=None
                for address in list(armed):
                    if address!=marker:remove(address)
                if completed==[12,13]:r['status']='two_operations_captured';save();break
            else:raise AssertionError(('Unpaired stop',hex(a)))
        else:raise AssertionError(('Unexpected stop',hex(a)))
        save();still=a in armed
        if still:remove(a)
        assert g.ask('s').startswith(('T','S'))
        if still:arm(a)
    else:r['status']='hit_limit'
except BaseException as e:r.update(status='capture_incomplete',error=repr(e),traceback=traceback.format_exc())
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for a in list(armed):remove(a)
            assert g.ask('Qqemu.PhyMemMode:0')=='OK';assert g.ask('qqemu.PhyMemMode')=='0';r['physical_mode_restored']=True
            g.send('c');r['guest_resumed']=True
        except BaseException as e:r['teardown_error']=repr(e)
        g.s.close()
    elif stopped:command(5186,'cont')
    r.update(ended_utc=utc(),armed_breakpoints_remaining=list(armed),pending_calls=len(pending),completed_intervals=completed)
    save()
    if lock:lock.close()
print(json.dumps({n:r[n] for n in ['status','error','pending_calls','completed_intervals','guest_resumed'] if n in r}))
