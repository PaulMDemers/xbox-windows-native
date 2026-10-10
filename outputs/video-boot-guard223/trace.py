"""Bounded prearmed actual TRUE reset guard; old base is a lead, never a grant."""
import datetime,hashlib,json,socket,struct,sys,time,traceback
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1]
assert case in ['control001','candidate001'];out=k/case
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/bootguard223-runs/nt5-bootguard223-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(ws/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text();ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
provider=read(ws/'outputs/video-reset-guard221/review.json')['providers'][case]
symbols=provider['symbols'];binary=ws/'outputs/video-boot-layout219/artifacts/build001'/case/'xboxbvid.dll'
assert sha(binary)==provider['sha256'];pe=pefile.PE(str(binary))
B=0xf8c00000;pe.relocate_image(B);entry=B+symbols['_ResetDisplay']
wrapper=B+symbols['_VidResetDisplay@4']
instructions=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(pe.get_data(wrapper-B,48),wrapper))
calls=[i for i in instructions if i.mnemonic=='call' and i.op_str==hex(entry)]
assert len(calls)==1
private_return=calls[0].address+calls[0].size
assert pe.get_data(wrapper-B,6)==bytes.fromhex('5589e583ec08')
assert pe.get_data(private_return-B,4)==bytes.fromhex('c9c20400')
reset_instructions=list(capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32).disasm(pe.get_data(entry-B,45),entry))
hal_calls=[i for i in reset_instructions if i.mnemonic=='call' and i.op_str=='dword ptr [eax + 0x2c]']
assert len(hal_calls)==1 and bytes(hal_calls[0].bytes)==bytes.fromhex('ff502c')
hal_call=hal_calls[0].address;hal_return=hal_call+hal_calls[0].size
r=dict(scope=__doc__,case=case,physical_access=False,ordinary_qualified=False,
       debugger=True,host_seeded_guard=True,base_lead=B,events=[],pins=[],guards=[],passed=False,started_utc=utc())
g=None;lock=None;stopped=False;armed=set();pairs={};frame=None;tail=None
pattern=bytes((i*73+(i>>8)*19+0x5b)&255 for i in range(0x15000))
def save():
    p=out/'trace.tmp';p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');p.replace(out/'trace.json')
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def arm(a):
    if a not in armed:g.bp(a);armed.add(a)
def remove(a):
    if a in armed:g.bp(a,False);armed.remove(a)
def blob(a,n):return b''.join(g.read(a+i,min(1024,n-i)) for i in range(0,n,1024))
def pin(a,n=64):
    assert B<=a and a+n<=B+pe.OPTIONAL_HEADER.SizeOfImage
    data=g.read(a,n);assert data==pe.get_data(a-B,n),('Resident provider/caller mismatch',hex(a))
    r['pins'].append(dict(address=a,rva=a-B,bytes=n,sha256=hashlib.sha256(data).hexdigest()))
def state():
    names=['_FrameBufferStart','_BackBuffer','_Owner','_References','_Ready']
    if '_BootWritableBytes' in symbols:names.append('_BootWritableBytes')
    return dict(globals={n:u32(B+symbols[n]) for n in names},published=list(struct.unpack('<11I',g.read(B+symbols['_Published'],44))))
def guard(label):
    data=blob(tail,len(pattern));p=out/'artifacts'/(label+'-tail.bin');p.write_bytes(data)
    saved=blob(u32(B+symbols['_BackBuffer'])+640*480,640*14)
    q=out/'artifacts'/(label+'-saved-rows.bin');q.write_bytes(saved)
    row=dict(stage=label,bytes=len(data),sha256=sha(p),guard_equal=data==pattern,zero_tail=not any(data),
             different_bytes=sum(a!=b for a,b in zip(data,pattern)),saved_rows_sha256=sha(q),state=state())
    r['guards'].append(row);return row
try:
    lock=acquire_monitor_lock(4594);command(4594,'stop');stopped=True
    g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    arm(entry);r['status']='prearmed_unvalidated_base_lead';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+180
    for hit in range(8):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                if time.monotonic()>=deadline:
                    g.s.settimeout(5);g.interrupt();stopped=True
                    raise TimeoutError('No complete TRUE reset within bounded capture')
        stopped=True;g.s.settimeout(5)
        regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
        a=regs['EIP'];assert a in armed
        row=dict(index=len(r['events']),utc=utc(),registers=regs);r['events'].append(row)
        if a==entry:
            # Actual code/header and TRUE argument must match BEFORE any mutation.
            assert g.read(B,2)==b'MZ';nt=u32(B+60);assert u32(B+nt+8)==provider['timestamp'] and u32(B+nt+80)==provider['image_size']
            pin(entry);row['set_mode']=u32(regs['ESP']+4)&255
            if not row['set_mode']:row['kind']='FALSE_reset_skipped';save();continue
            assert row['set_mode']==1;remove(entry);row['kind']='actual_TRUE_private_entry'
            ret=u32(regs['ESP']);pin(ret,16);pin(wrapper,48)
            assert ret==private_return and regs['ESP']==regs['EBP']-12
            wrapper_stack=regs['EBP']+4;public_return=u32(wrapper_stack)
            assert u32(wrapper_stack+4)&255==1;pin(public_return,16)
            r['before_seed']=state();frame=r['before_seed']['globals']['_FrameBufferStart'];back=r['before_seed']['globals']['_BackBuffer']
            assert frame and frame%4096==0
            assert back-frame==(0x39dd00 if case=='candidate001' else 0x3b2d00)
            view=r['before_seed']['published'];assert view[2]==frame and view[3]==0x3c00000 and view[4]==0x400000 and view[10]==0
            if case=='candidate001':assert r['before_seed']['globals']['_BootWritableBytes']==0x3eb000
            tail=frame+0x3eb000;r['tail_start']=tail;r['indexed_end']=back+316160
            assert r['indexed_end']==(tail if case=='candidate001' else frame+0x400000)
            pteaddr=0xc0000000+(tail>>12)*4;ptes=list(struct.unpack('<21I',g.read(pteaddr,84)))
            assert ptes==list(struct.unpack('<21I',g.read(pteaddr,84)))
            for i,pte in enumerate(ptes):assert pte&1 and pte&16 and pte&0xfffff000==0x03feb000+i*4096
            r['tail_mapping']=dict(pte_address=pteaddr,ptes=ptes,physical_start=0x03feb000,physical_end=0x4000000)
            for i in range(0,len(pattern),1024):g.write(tail+i,pattern[i:i+1024])
            assert guard('seeded_TRUE_entry')['guard_equal']
            pairs[ret]=dict(function='ResetDisplay',stack=regs['ESP'],delta=4);arm(ret)
            pairs[public_return]=dict(function='VidResetDisplay',stack=wrapper_stack,delta=8);arm(public_return)
            pin(hal_call,16);arm(hal_call);arm(hal_return)
        elif a==hal_call:
            row.update(kind='HAL_callback_call_site',stack=regs['ESP'],table=regs['EAX'],target=u32(regs['EAX']+0x2c))
            row['guard']=guard('before-HAL-callback');assert row['guard']['guard_equal']
            r['hal_pair']=dict(stack=regs['ESP'],target=row['target']);remove(a)
        elif a==hal_return:
            assert regs['ESP']==r['hal_pair']['stack'];remove(a)
            row.update(kind='HAL_callback_return_site',pair=r['hal_pair'])
            row['guard']=guard('after-HAL-callback')
        elif a in pairs:
            pair=pairs.pop(a);assert regs['ESP']==pair['stack']+pair['delta'];remove(a)
            row.update(kind='actual_paired_return',function=pair['function'],pair=pair)
            row['guard']=guard(pair['function']+'-return')
            if pair['function']=='ResetDisplay':
                assert row['guard']['guard_equal'] if case=='candidate001' else row['guard']['zero_tail']
                # Public pair uses its actual EBP frame saved at entry, not the
                # private cdecl return stack, which still contains the argument.
                assert len(pairs)==1
            else:
                assert pair['function']=='VidResetDisplay' and not pairs
                assert row['guard']['guard_equal'] if case=='candidate001' else row['guard']['zero_tail']
                assert state()==r['before_seed']
                r.update(passed=True,status='actual_TRUE_reset_guard_observed');save();break
        save()
    else:raise RuntimeError('Bounded hit limit')
except BaseException as exc:r.update(error=repr(exc),status='preserved_trace_failure',host_traceback=traceback.format_exc());save()
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
    if lock:lock.close()
    r.update(closed=True,remaining_breakpoints=sorted(armed),closed_utc=utc());save();(out/'trace-finished.signal').touch(exist_ok=False)
print(json.dumps({n:r[n] for n in ['passed','status','closed','guest_resumed','error'] if n in r}))
