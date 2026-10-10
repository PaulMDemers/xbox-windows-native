"""Bounded debugger capture of unchanged FATX source buffers and child completions."""
import datetime, hashlib, json, socket, struct, sys, time, traceback
from pathlib import Path

k=Path(__file__).resolve().parent; repo=k.parents[1]; case=sys.argv[1]
assert case in ['emu001','emu002']
run=repo/('work/runs/nt5storbuf-'+case); out=k/case; art=out/'artifacts'
art.mkdir(parents=True,exist_ok=True)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
assert not (out/'trace.json').exists()
canon=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canon/'work/python-packages'),str(repo/'outputs/native-windows-prebuild')]
import pefile
from monitor_capture import command,acquire_monitor_lock
code=(repo/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text(); ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns)
Remote=ns['Remote']; review=json.loads((k/'sites.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
lp=repo/'outputs/fatx-install-buffer/write-layouts.json'
assert sha(lp.read_bytes())==review['layouts_sha256']
L=json.loads(lp.read_text())['offsets']
pub=json.loads((repo/'outputs/native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
owner=json.loads((repo/'outputs/shutdown-popup-workload/site-review.json').read_text())['thread_owner_offset']
P=json.loads((repo/'outputs/native-windows-nt5-kernel/process-layouts.json').read_text())['_EPROCESS']['fields']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(physical_access=False,ordinary_qualified=False,source_sha256=sha(Path(__file__).read_bytes()),
       sites_sha256=sha((k/'sites.json').read_bytes()),started_utc=utc(),events=[],hit_counts={},
       limits='Debugger changes timing. Child IRP plus submission generation identifies asynchronous requests. Physical MDL bytes are observed before dispatch and at completion, not an emulator DMA-buffer capture.')
g=None; armed=set(); fixed={}; active={}; returns={}; expanded=False; stopped=False
completed_writes=0; next_id=1; lock=acquire_monitor_lock(5124)

def save():
    p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def read(p,n):
    return b''.join(g.read(p+i,min(512,n-i)) for i in range(0,n,512))
def u32(p):return struct.unpack('<I',read(p,4))[0]
def i64(p):return struct.unpack('<q',read(p,8))[0]
def uni(p):
    n,m,b=struct.unpack('<HHI',read(p,8));assert n<=m and n<=2048 and n%2==0
    return read(b,n).decode('utf-16le') if n else ''
def context(ctx):
    file=u32(ctx+L['context_file']); fcb=u32(file+L['file_fcb'])
    return file,fcb,uni(fcb+L['fcb_path'])
def target(path):return path.lower().endswith('\\xwnctl\\payload2.txt')
def who(thread):
    proc=u32(thread+owner)
    return dict(thread=hex(thread),process=hex(proc),pid=u32(proc+P['UniqueProcessId']['offset']),
                image=read(proc+P['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii','replace'))
def blob(data):
    digest=sha(data);p=art/(digest+'.bin')
    if not p.exists():p.write_bytes(data)
    return dict(sha256=digest,bytes=len(data),artifact=p.name)
def virtual(p,n):
    if not p or not 0<n<=4096:return dict(address=hex(p),unobserved='outside capture bounds',length=n)
    try:return dict(address=hex(p),**blob(read(p,n)))
    except Exception as exc:return dict(address=hex(p),error=repr(exc),length=n)
def mdl(p,n):
    if not p:return dict(absent=True)
    raw=read(p,28);nxt,size,flags,process,mapped,start,count,offset=struct.unpack('<IHHIIIII',raw)
    assert offset<4096 and n<=count and 0<n<=4096 and size>=28
    pages=(offset+n+4095)//4096;assert pages<=2 and size>=28+pages*4
    pfns=list(struct.unpack('<'+'I'*pages,read(p+28,pages*4)))
    assert all(v<16384 for v in pfns),pfns
    vaddr=mapped if flags&5 and mapped else start+offset
    row=dict(address=hex(p),raw_header=raw.hex(),flags=flags,byte_count=count,byte_offset=offset,
             pfns=pfns,virtual=virtual(vaddr,n),virtual_mapping_flag=bool(flags&5))
    data=bytearray();remaining=n;within=offset
    assert g.ask('Qqemu.PhyMemMode:1')=='OK'
    try:
        for page in pfns:
            take=min(remaining,4096-within);data.extend(read(page*4096+within,take));remaining-=take;within=0
    finally:assert g.ask('Qqemu.PhyMemMode:0')=='OK'
    assert remaining==0
    row['physical']=blob(bytes(data));row['virtual_equals_physical']=row['virtual'].get('sha256')==row['physical']['sha256']
    return row
def emit(kind,**fields):
    row=dict(sequence=len(r['events']),kind=kind,utc=utc(),**fields);r['events'].append(row);return row
def check_loaded(name,base,digest):
    path=k/'artifacts'/name;assert sha(path.read_bytes())==digest
    pe=pefile.PE(str(path)); delta=(base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff
    image=bytearray(pe.get_memory_mapped_image())
    for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]):
        for e in block.entries:
            if e.type==3:struct.pack_into('<I',image,e.rva,(struct.unpack_from('<I',image,e.rva)[0]+delta)&0xffffffff)
            else:assert e.type==0
    sections=[]
    for section in pe.sections:
        if section.Characteristics&0x20000000 and not section.Characteristics&0x02000000:
            pages=[];at=section.VirtualAddress;left=section.Misc_VirtualSize
            nonpaged=bool(section.Characteristics&0x08000000)
            while left:
                n=min(left,4096-((base+at)&4095));expected=bytes(image[at:at+n])
                r['verification_step']=dict(module=name,section=section.Name.decode('ascii','replace'),address=base+at,bytes=n);save()
                page=dict(rva=at,bytes=n,expected=sha(expected))
                try:
                    actual=read(base+at,n);page.update(loaded=sha(actual),exact=actual==expected)
                    assert actual==expected,dict(module=name,rva=at,reason='loaded executable bytes differ')
                except AssertionError as exc:
                    if str(exc)!='E14' or nonpaged:raise
                    page['unavailable']='Nonresident pageable code; not traced or claimed verified'
                pages.append(page);at+=n;left-=n
            sections.append(dict(name=section.Name.rstrip(b'\0').decode(),nonpaged=nonpaged,pages=pages))
    assert sections and any(v['nonpaged'] for v in sections)
    assert all(p.get('exact') for section in sections if section['nonpaged'] for p in section['pages'])
    return dict(name=name,base=hex(base),disk_sha256=digest,sections=sections,
                qualification='All nonpaged executable bytes and all readable pageable bytes must match after relocation. Nonresident pageable ranges remain explicitly unverified; all trace sites are separately checked.')

def discover():
    K=review['kernel_base_expected'];r['verification_step']='kernel_header';save();assert read(K,2)==b'MZ'
    pe=K+u32(K+60);assert read(pe,4)==b'PE\0\0' and u32(pe+8)==review['kernel_timestamp']
    head=K+pub['_PsLoadedModuleList']['rva'];link=u32(head);modules=[];seen=set()
    while link!=head:
        assert link not in seen and len(seen)<128;seen.add(link)
        modules.append(dict(name=uni(link+44),base=u32(link+24),size=u32(link+32)));link=u32(link)
    r['modules']=modules;r['verification_step']='loaded_code';save()
    bases={v['name'].lower():v['base'] for v in modules}
    r['loaded_binary_checks']=[check_loaded('xwnfatx.sys',bases['xwnfatx.sys'],review['driver_sha256']),
                               check_loaded('atapi.sys',bases['atapi.sys'],review['ata_sha256'])]
    D=bases['xwnfatx.sys'];delta=(D-review['preferred_base'])&0xffffffff
    for site in review['sites']:
        b=bytearray.fromhex(site['bytes'])
        for offset in site['relocations']:struct.pack_into('<I',b,offset,(struct.unpack_from('<I',b,offset)[0]+delta)&0xffffffff)
        address=D+site['rva'];assert read(address,len(b))==b
        fixed[address]=dict(**site,loaded_bytes=bytes(b).hex())
    r['modules']=modules;r['driver_base']=D

try:
    command(5124,'stop');stopped=True;g=Remote(5125);g.s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    assert g.ask('Qqemu.PhyMemMode:0')=='OK'
    gate=review['ntwrite_gate']['address'];g.bp(gate);armed.add(gate)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+240
    for hit in range(30000):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(1)
            try:g.recv();break
            except TimeoutError:
                if (out/'trace-stop.signal').exists() or time.monotonic()>=deadline:
                    g.s.settimeout(5);g.interrupt();r['status']='capture_deadline';break
        stopped=True;g.s.settimeout(5)
        if r['status']=='capture_deadline':break
        regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
        a=regs['EIP'];assert a in armed
        if a==gate:
            assert read(a,len(bytes.fromhex(review['ntwrite_gate']['bytes']))).hex()==review['ntwrite_gate']['bytes']
            discover();name='discovery';r['status']='loaded_binaries_verified'
        else:
            thread=u32(0xffdff124);key=(thread,regs['EBP'],a)
            if a not in fixed:
                name='dispatch_return';request=returns.pop(key,None)
                if request:emit(name,request_id=request['id'],child_irp=hex(request['child']),status=regs['EAX'],completion_already_observed=request['child'] not in active,**who(thread))
            else:
                site=fixed[a];name=site['name'];kind=site['kind']
                assert read(a,len(bytes.fromhex(site['loaded_bytes']))).hex()==site['loaded_bytes']
                if kind=='entry':
                    ctx=u32(u32(regs['ESP']+4));file,fcb,path=context(ctx)
                    if target(path):
                        expanded=True;irp=u32(ctx);stack=u32(ctx+32);n=u32(stack+4);mp=u32(irp+4)
                        emit('source_entry',context=hex(ctx),parent_irp=hex(irp),path=path,file_offset=i64(stack+12),length=n,irp_flags=u32(irp+8),
                             buffer=mdl(mp,n) if mp else virtual(u32(irp+60),n),**who(thread))
                elif kind=='buffer':
                    ctx=u32(regs['EBP']-100);file,fcb,path=context(ctx)
                    if target(path):emit('buffer_ready',context=hex(ctx),parent_irp=hex(u32(ctx)),file_offset=i64(regs['EBP']-96),buffer=virtual(regs['EAX'],u32(regs['EBP']-124)),**who(thread))
                elif kind in ['read_submit','write_submit']:
                    ctx=u32(regs['EBP']+8);assert ctx==regs['EBX'];file,fcb,path=context(ctx)
                    if target(path):
                        child=regs['EDX'];assert child==regs['EDI'] and child not in active
                        parent=u32(ctx);n=u32(regs['EBP']+16);offset=i64(u32(regs['EBP']+12));stack=u32(child+96)-36
                        assert read(stack,1)[0]==(3 if kind=='read_submit' else 4)
                        assert u32(stack+4)==n and i64(stack+12)==offset and u32(stack+32)==ctx
                        request=dict(id=next_id,child=child,context=ctx,length=n,operation=kind);next_id+=1;active[child]=request
                        retkey=(thread,regs['EBP'],a+6);assert retkey not in returns;returns[retkey]=request
                        emit(kind,request_id=request['id'],child_irp=hex(child),context=hex(ctx),parent_irp=hex(parent),
                             disk_relative_offset=offset,expected_absolute_offset=8004132864+offset,length=n,buffer_offset=u32(regs['EBP']+20),
                             wait=bool(u32(regs['EBP']+24)&255),child_flags=u32(child+8),parent_flags=u32(parent+8),
                             context_refcount=u32(ctx+44),event_signal_state=u32(ctx+52),buffer=mdl(u32(child+4),n),**who(thread))
                elif kind=='completion':
                    child=u32(regs['ESP']+8);ctx=u32(regs['ESP']+12);request=active.pop(child,None)
                    if request:
                        assert ctx==request['context']
                        emit('completion',request_id=request['id'],operation=request['operation'],child_irp=hex(child),context=hex(ctx),
                             status=u32(child+24),information=u32(child+28),context_refcount=u32(ctx+44),event_signal_state=u32(ctx+52),
                             buffer=mdl(u32(child+4),request['length']),**who(thread))
                        if request['operation']=='write_submit':completed_writes+=1
        r['hit_counts'][name]=r['hit_counts'].get(name,0)+1
        if r['events'] or hit%100==0:save()
        g.bp(a,False);armed.remove(a);assert g.ask('s').startswith(('T','S'))
        if completed_writes>=12 and not active and not returns:r['status']='bounded_requests_complete';break
        desired={p for p,s in fixed.items() if expanded or s['kind']=='entry'}|{v[2] for v in returns}
        if not fixed:desired.add(gate)
        for p in armed-desired:g.bp(p,False)
        armed &= desired
        for p in desired-armed:g.bp(p);armed.add(p)
        if time.monotonic()>=deadline:r['status']='capture_deadline';break
    else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc),traceback=traceback.format_exc())
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            assert g.ask('Qqemu.PhyMemMode:0')=='OK'
            for p in list(armed):g.bp(p,False);armed.remove(p)
            g.send('c');r['guest_resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
        g.s.close()
    elif stopped:command(5124,'cont')
    r.update(ended_utc=utc(),completed_writes=completed_writes,outstanding_requests=list(active.values()),pending_dispatch_returns=len(returns),armed_breakpoints_remaining=list(armed))
    save();lock.close();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['status','error','completed_writes','guest_resumed'] if n in r}))
