"""One bounded no-release standalone run. Only breakpoints and host control write."""
import datetime,hashlib,json,re,socket,struct,time,traceback,sys
from pathlib import Path
from protocol import Remote,monitor
from objects import inspect as inspect_objects,commands
from backend import Backend
from proof import vertices
from model import state,translate,disjoint,oracle
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu001';out=k/case;root=Path('E:/xwn275')/case;private=root/'private'
assert (root/'instance.json').exists() and not (out/'trace.json').exists()
review=json.loads((k.parent/'owned-texture271/binary-review005.json').read_text());symbols=json.loads((out/'symbols.json').read_text())
xbe=(root/'default.xbe').read_bytes();checkpoint=review['checkpoint']['va'];record=symbols['_record271']
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(started_utc=utc(),checkpoints=[],monitor=[],breakpoints=[],physical_reads=[],passed=False,physical_access=False,release_installed=False,observer_operation=True,guest_memory_writes=False,guest_register_writes=False,ordinary_qualified=False,full_lifetime_qualified=False)
g=None;point=False;stopped=True;physical=False;backend=None
def save():
    p=out/'trace.partial.json';p.write_text(json.dumps(r,indent=2)+'\n');p.replace(out/'trace.json')
def cmd(s,quit=False):
    reply=monitor(4754,s,quit);r['monitor'].append(dict(command=s,reply=reply,utc=utc()));save();return reply
def bp(add):
    global point
    if add:point=True
    q=f'{"Z" if add else "z"}1,{checkpoint:x},1';reply=g.ask(q);r['breakpoints'].append(dict(command=q,reply=reply));save();assert reply=='OK'
    if not add:point=False
def phys(a,n):
    global physical
    assert stopped and 0<n<=4096 and 0<=a and a+n<=0x4000000
    assert g.ask('Qqemu.PhyMemMode:1')=='OK';physical=True
    try:
        data=g.read(a,n);r['physical_reads'].append(dict(address=a,bytes=n,sha256=sha(data),hex=data.hex() if n<=8 else None));return data
    finally:
        assert g.ask('Qqemu.PhyMemMode:0')=='OK';physical=False
def word(a):return struct.unpack('<I',g.read(a,4))[0]
def registers():
    text=cmd('info registers');d={n:int(v,16) for n,v in re.findall(r'\b(EIP|ESP|CR0|CR3|CR4)=([0-9a-fA-F]+)',text)}
    assert all(n in d for n in ('EIP','ESP','CR0','CR3','CR4'))
    assert struct.unpack_from('<I',bytes.fromhex(g.ask('g')),32)[0]==d['EIP'];return d,text
def capture(row,regs):
    # Persist each raw observation before validation; all kernel/source bytes private.
    prefix='stop'+str(len(r['checkpoints']))
    def read(a,n,label):
        data=g.read(a,n);p=private/(prefix+'-'+label+'.bin');assert not p.exists();p.write_bytes(data)
        row.setdefault('reads',[]).append(dict(label=label,address=a,bytes=n,sha256=sha(data),private_file=str(p)));save();return data
    assert regs['EIP']==checkpoint and regs['CR0']&0x80000000
    assert read(checkpoint,19,'checkpoint')==bytes.fromhex(review['checkpoint']['bytes'])
    stack=struct.unpack('<4I',read(regs['ESP'],16,'stack'));caller,phase,p,cookie=stack
    row['arguments']=dict(caller=caller,phase=phase,record=p,cookie=cookie);save()
    assert p==record and cookie==0x271c0de
    call=next(c for c in review['callsites'] if c['va']+5==caller)
    assert read(caller-5,5,'caller')==bytes.fromhex(call['bytes'])
    header=read(0x10000,4096,'xbe-header');assert header[:4]==b'XBEH'
    for off in (0x104,0x108,0x10c,0x11c,0x120):assert header[off:off+4]==xbe[off:off+4],('XBE header',off)
    table=struct.unpack_from('<I',header,0x120)[0]-0x10000
    row['section_reference_counts']=[]
    for i in range(4):
        at=table+56*i
        assert header[at:at+24]==xbe[at:at+24] and header[at+28:at+56]==xbe[at+28:at+56]
        refs=struct.unpack_from('<I',header,at+24)[0];row['section_reference_counts'].append(refs)
        assert refs==1,'Expected one preload reference in this standalone XBE'
    save()
    section=review['sections'][0];assert section['name']=='.text'
    assert sha(read(section['va'],section['raw_size'],'text'))==section['sha256'],'Loaded text differs'
    data=read(record,1612,'record');h=struct.unpack_from('<43I',data);row['state_header']=list(h);save()
    previous=0 if len(r['checkpoints'])==1 else r['checkpoints'][-2]['arguments']['phase']
    row['pixel_check']={}
    try:row['pixel_check']=state(data,phase,previous)
    except AssertionError as e:row['pixel_check']=dict(passed=False,error=repr(e))
    save()
    # Resolve actual Xbox kernel from the loader-filled import, not an NT5 address.
    imported=word(symbols['__imp__MmGetPhysicalAddress@4']);row['physical_address_import']=imported;save()
    assert 0x80000000<=imported<0x80400000
    candidates=[]
    for base in range(imported&~0xfff,max(0x80000000,(imported&~0xfff)-0x100000)-1,-4096):
        if g.read(base,2)!=b'MZ':continue
        off=word(base+60)
        if 64<=off<=2048 and g.read(base+off,4)==b'PE\0\0':
            image_size=word(base+off+80)
            if 0x10000<image_size<=0x200000 and base<=imported<base+image_size:
                candidates.append(base);row['kernel_candidates']=list(candidates);save();break
    assert len(candidates)==1,('Kernel PE candidates',candidates)
    kb=candidates[0];kh=read(kb,4096,'kernel-header');po=struct.unpack_from('<I',kh,60)[0]
    assert struct.unpack_from('<H',kh,po+4)[0]==0x14c
    size=struct.unpack_from('<I',kh,po+80)[0];assert 0x10000<size<=0x200000 and kb<=imported<kb+size
    exr,exn=struct.unpack_from('<II',kh,po+120);assert 0<exr<size and exn<size
    ex=read(kb+exr,40,'kernel-export');ordinal,nf,nn,functions=struct.unpack_from('<4I',ex,16)
    assert 0<nf<=1024 and functions+nf*4<=size
    funcs=struct.unpack('<'+'I'*nf,read(kb+functions,nf*4,'kernel-functions'))
    matches=[ordinal+i for i,v in enumerate(funcs) if kb+v==imported];assert len(matches)==1
    read(imported,64,'kernel-physical-function')
    row['kernel']=dict(base=kb,size=size,export_ordinal=matches[0],timestamp=struct.unpack_from('<I',kh,po+8)[0],identity_scope='Runtime PE/export/instruction hashes plus pinned BIOS; not a symbol-matched NT5 kernel')
    # An early error may precede allocation; preserve and continue the terminal.
    if phase==255:save();return phase
    ranges=[];translations=[]
    def extent(name,va,pa,n):
        assert 0<va<=0xffffffff-n and 0<pa and n>0
        points=sorted(set([va,va+n-1]+list(range((va+4095)&~4095,va+n,4096))))
        for a in points:
            translated,detail=translate(phys,regs['CR3'],regs['CR4'],a)
            assert translated==pa+a-va,(name,hex(a),hex(translated),hex(pa))
            translations.append(dict(name=name,virtual=a,physical=translated,**detail))
        ranges.append((name,pa,n))
    for u in range(4):
        assert h[14+u]==h[6+u]+256 and h[18+u]==h[10+u]+256
        extent('texture'+str(u),h[6+u],h[10+u],4096)
        source=read(h[6+u],4096,'texture'+str(u));assert source==oracle.blocks()[u],('Source guard',u)
    extent('vertices',h[31],h[33],384);assert read(h[31],384,'vertices')==vertices()
    assert 2560<=h[29]<=4096 and h[30]==480
    extent('target',h[27],h[28],h[29]*h[30])
    # Actual pbkit state, backed by the pinned loaded instruction section.
    names=['_pb_DmaBuffer2','_pb_DmaBuffer7','_pb_DmaBuffer8','_pb_DepthStencilPitch','_pb_Head','_pb_Tail','_pb_Size','_pb_Put','_pb_DmaUserAddr','_pb_FifoChannelID','_pb_FifoHTAddr','_pb_GrCtxID','_pb_GrCtxInst','_pb_GrCtxTableInst','_pb_GpuInstMem','_pb_FreeInst','_pb_FifoBigInst','_pb_FBSize','_pb_DSAddr','_pb_DSSize']
    pb={name:word(symbols[name]) for name in names};row['pbkit']=pb;save()
    head=pb['_pb_Head'];sz=pb['_pb_Size'];assert 65536<sz<=4*1024**2 and sz&(sz-1)==0
    assert pb['_pb_Tail']==head+sz and head<=pb['_pb_Put']<=head+sz
    headpa,_=translate(phys,regs['CR3'],regs['CR4'],head);extent('pushbuffer',head,headpa,sz+8192)
    row['push_commands']=commands(read(head,pb['_pb_Put']-head,'pushbuffer-used'));save()
    assert 0<=pb['_pb_FifoChannelID']<=1 and pb['_pb_DmaUserAddr']==0xfd800000+(pb['_pb_FifoChannelID']<<16)
    inst=pb['_pb_GrCtxInst'];tableinst=pb['_pb_GrCtxTableInst'];free=pb['_pb_FreeInst']
    assert 0x1000<=tableinst<inst<free<=0x2000
    tabledata=read(0xfd700000+(tableinst<<4),8,'context-table')
    assert struct.unpack_from('<I',tabledata,4*pb['_pb_FifoChannelID'])[0]==inst
    assert 0x710000<=pb['_pb_FifoHTAddr']<0x720000
    ramht=read(0xfd000000+pb['_pb_FifoHTAddr'],4096,'ramht')
    row['objects']=inspect_objects(ramht,pb,h,lambda a,n,label:read(a,n,label));save()
    read(0xfd700000+(inst<<4),min(0x37f0,(free-inst)*16),'graphics-context')
    gpu=pb['_pb_GpuInstMem'];gpu_pa,_=translate(phys,regs['CR3'],regs['CR4'],gpu)
    assert 0x3f00000<=gpu_pa<0x4000000
    extent('conservative-instance-tail',gpu,gpu_pa,0x4000000-gpu_pa)
    disjoint(ranges);row['translations']=translations;row['ranges']=ranges
    row['ownership_scope']='Loaded owned pbkit code and actual allocation/channel/context/RAMHT ranges; no host seven-family ledger, four-generation lifetime or native Windows GPU grant'
    save();return phase
try:
    backend=Backend(cmd,out,root,r,save)
    g=Remote(4755);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0';bp(True)
    deadline=time.monotonic()+400
    for index in range(4):
        g.send('c');stopped=False
        stop=g.recv(min(100,max(1,deadline-time.monotonic())));stopped=True
        regs,text=registers();row=dict(stop=stop,utc=utc(),registers=regs,register_text=text);r['checkpoints'].append(row);save()
        bp(False);phase=capture(row,regs)
        if phase in (33,255):
            r['terminal_phase']=phase;r['passed']=backend.completed and phase==33 and len(r['checkpoints'])==3 and all(x['pixel_check'].get('passed') for x in r['checkpoints']);break
        assert phase==(11 if index==0 else 22)
        assert row['pixel_check'].get('passed'),'Native pixel control failed before observer request'
        if phase==11:backend.begin()
        else:backend.end()
        # Step only the original first instruction past the removed breakpoint.
        g.send('s');stopped=False;row['step']=g.recv();stopped=True;bp(True)
    else:raise AssertionError('Checkpoint bound exhausted')
except BaseException as e:
    r['error']=repr(e);r['traceback']=traceback.format_exc();save()
finally:
    try:
        if g:
            if not stopped:r['cleanup_interrupt']=g.interrupt();stopped=True
            if physical:assert g.ask('Qqemu.PhyMemMode:0')=='OK';physical=False
            if point:bp(False)
            r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0'
            if backend:
                try:backend.cleanup()
                except BaseException as e:r['frontend_cleanup_error']=repr(e);r['passed']=False
            if r['passed']:g.send('c');stopped=False
            else:r['quarantined_until_owned_exit']=True
            g.s.close();g=None
            r['resumed_after_teardown']=bool(r['passed']);save()
            # Permit the native terminal's explicit15second halt interval.
            if r['passed']:time.sleep(18)
        r['final_status']=cmd('info status');cmd('screendump '+json.dumps((private/'screen.ppm').as_posix()))
        cmd('stop');r['host_quit']=cmd('quit',quit=True);r['orderly_quit_sent']=True
    except BaseException as e:r['cleanup_error']=repr(e)
    r.update(remaining_breakpoint=point,physical_mode_remaining=physical,ended_utc=utc());save()
print(json.dumps({key:r.get(key) for key in ['passed','terminal_phase','error','cleanup_error','orderly_quit_sent']},indent=2))
