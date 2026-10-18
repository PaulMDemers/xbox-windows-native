"""One owned emulator launch; read-only original handoff trace, bounded teardown."""
import ast
import io
import datetime
import ftplib
import hashlib
import json
import re
import struct
import sys
import time
from pathlib import Path
from protocol003 import Remote, monitor
from contracts import plan,arguments,returned
from trampoline import observe_trampoline
from entry_decode import decode as decode_entry

K = Path(__file__).resolve().parent
W = K.parents[1]
O = K / 'emu001'
RUN = Path('C:/xwn513/runs/nt5-entry513-emu001')
PRIVATE = Path('C:/xwn513/trace001')
sys.path.insert(0, str(W / 'outputs/surface-bridge260'))
from atomic_json import write_json
assert not (O / 'trace.json').exists() and not PRIVATE.exists()
PRIVATE.mkdir()
build=json.loads((K.parent/'entry-trampoline510/build001.json').read_text())
sym=build['wrapper_symbols']
assert json.loads((K.parent/'return-transport506/host003.json').read_text())['passed']
xbe=Path('C:/xwn510/build001/default.xbe').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(xbe)==build['sha256']
calls=plan(xbe,sym)
utc = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
r = dict(started_utc=utc(), physical_access=False, ordinary_qualified=False,
         checkpoints=[], breakpoints=[], reads=[], monitor=[], passed=False,
         guest_memory_or_register_writes=False, new_physical_launch=False)
g = None
active = set()
physical_mode = False
stopped = False


def save():
    write_json(O / 'trace.json', r)


def mon(command):
    reply = monitor(6134, command)
    r['monitor'].append(dict(command=command, reply=reply, utc=utc()))
    save()
    return reply


def bp(address, add):
    if add:
        active.add(address)
    command = f'{"Z" if add else "z"}1,{address:x},1'
    reply = g.ask(command)
    r['breakpoints'].append(dict(command=command, reply=reply))
    save()
    assert reply == 'OK'
    if not add:
        active.remove(address)


def capture(address, length, label, physical=False):
    global physical_mode
    assert stopped and 0 < length <= 1048576
    if physical:
        assert 0 <= address and address+length <= 0x4000000
        assert g.ask('Qqemu.PhyMemMode:1') == 'OK'
        physical_mode = True
    try:
        data = b''.join(g.read(address+i, min(65536, length-i)) for i in range(0, length, 65536))
        path = PRIVATE / f'{len(r["reads"]):03d}-{label}.bin'
        path.write_bytes(data)
        r['reads'].append(dict(address=address, bytes=length, physical=physical,
                              label=label, private_file=str(path), sha256=sha(data)))
        save()
        return data
    finally:
        if physical_mode:
            assert g.ask('Qqemu.PhyMemMode:0') == 'OK'
            physical_mode = False


def registers(label):
    text = mon('info registers')
    d = {n: int(v, 16) for n, v in re.findall(r'\b(EIP|ESP|EAX|EBX|EBP|EDI|ESI|EDX|ECX|EFL|CR0|CR3|CR4)=([0-9a-fA-F]+)', text)}
    assert all(n in d for n in ('EIP', 'CR0', 'CR3', 'CR4', 'EDX', 'ESI', 'ECX'))
    assert struct.unpack_from('<I', bytes.fromhex(g.ask('g')), 32)[0] == d['EIP']
    row = dict(label=label, utc=utc(), registers=d, raw_registers=text)
    r['checkpoints'].append(row)
    save()
    return row


def translate(va, regs, label):
    assert regs['CR0'] & 0x80000000 and not regs['CR4'] & 0x20
    pde = struct.unpack('<I', capture((regs['CR3'] & 0xfffff000)+(va >> 22)*4, 4, label+'-pde', True))[0]
    assert pde & 1
    if pde & 0x80:
        assert regs['CR4'] & 0x10
        return (pde & 0xffc00000)+(va & 0x3fffff)
    pte = struct.unpack('<I', capture((pde & 0xfffff000)+((va >> 12) & 1023)*4, 4, label+'-pte', True))[0]
    assert pte & 1
    return (pte & 0xfffff000)+(va & 4095)


def await_stop(address, label):
    global stopped
    reply = g.recv(35)
    stopped = True
    assert reply.startswith(('T', 'S')), reply
    row = registers(label)
    assert row['registers']['EIP'] == address
    bp(address, False)
    return row


def advance(address, label):
    global stopped
    bp(address, True)
    stopped = False
    g.send('c')
    return await_stop(address, label)


class ActualCalls:
    def __init__(self,handlers):self.handlers=handlers
    def stop(self,address,label):
        bp(sym['entry498_abort'],True)
        try:return advance(address,label)['registers']
        finally:
            if stopped and sym['entry498_abort'] in active:bp(sym['entry498_abort'],False)
    def read(self,address,length,label):return capture(address,length,label)
    def record(self,row):
        r.setdefault('calls',{})[row['label']]=row.copy();save()

    def verify_entry(self,regs):
        for name in ('EAX','EBX','ECX','EDX','ESI','EDI','EBP','ESP','EFL'):assert regs[name]==entry['registers'][name],name
        assert struct.unpack('<3I',capture(sym['entry503_status'],12,'initial-indicator-status'))==(0,0,0)
    def verify_complete(self,regs):
        assert struct.unpack('<I',capture(sym['entry498_state'],4,'final-state'))[0]==7
        original=entry['registers']
        for name in ('EAX','EBX','ECX','EDX','ESI','EDI','EBP','ESP','EFL'):assert original[name]==regs[name],name
        receipt=capture(sym['entry498_record'],112,'entry-memory-receipt');decoded=decode_entry(receipt)
        assert decoded['flags']==original['EFL']
        for name,value in decoded['registers'].items():assert value==original[name.upper()]
        for name,value in decoded['selectors'].items():
            match=re.search(r'\b'+name.upper()+r'\s*=([0-9a-fA-F]+)',entry['raw_registers']);assert match and int(match.group(1),16)==value
        r['entry_receipt']=decoded;save()
    def verify_terminal(self):
        status=struct.unpack('<6I',capture(sym['entry503_status'],24,'terminal-indicator-status'));assert status==(0,)*6
        assert struct.unpack('<I',capture(sym['entry503_state'],4,'terminal-indicator-state'))[0]==2
        assert struct.unpack('<2I',capture(sym['entry503_restore_attempted'],8,'terminal-return-state'))==(1,1)
        restored=struct.unpack('<9I',capture(sym['entry503_restored'],36,'terminal-restored-registers'))
        assert restored==tuple(entry['registers'][n] for n in ['EDI','ESI','EBP','ESP','EBX','EDX','ECX','EAX','EFL'])
        r['terminal_status']=list(status);save()

save()
try:
    from kernel_calls import observe
    deadline=time.monotonic()+65
    while not (RUN/'startup-ready.json').exists():
        assert time.monotonic()<deadline and not (RUN/'cleanup.json').exists()
        time.sleep(.25)
    tree=ast.parse((W/'outputs/native-windows-prebuild/launch_unleashx.py').read_text(encoding='utf-8'))
    login=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='login')
    credentials=[ast.literal_eval(arg) for arg in login.args]
    while True:
        f=ftplib.FTP()
        try:
            f.connect('127.0.0.1',6136,timeout=3);f.login(*credentials);break
        except ftplib.all_errors:
            f.close();assert time.monotonic()<deadline;time.sleep(.5)
    prepared=json.loads((K/'preparation001.json').read_text());assert prepared['status']=='prepared'
    assert prepared['change']['sha256']==sha(xbe)
    mon('stop');stopped=True;g=Remote(6135)
    r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
    bp(0x11100,True);g.send('c');stopped=False
    r['launch']=dict(requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNBoot510a\default.xbe');save()
    try:
        f.sock.settimeout(20);r['launch']['reply']=f.sendcmd(r['launch']['command'])
    except ftplib.all_errors as e:r['launch']['reply_uncertain']=type(e).__name__
    finally:f.close()
    low=await_stop(0x11100,'trampoline-entry')
    entry,proof=observe_trampoline(low,xbe,capture,advance,bp)
    r['trampoline']=proof;save()
    # Header mutable loader fields are retained as evidence, not required equal.
    capture(0x10000,4096,'loaded-xbe-header')
    for address,length,label in [(sym['entry498_gate'],929,'entry-code'),(sym['entry498_record'],320,'entry-data'),(sym['_start'],64,'original-start-code')]:
        assert capture(address,length,label)==xbe[address-0x10000:address-0x10000+length]
    thunks=struct.unpack('<11I',capture(0x11000,44,'resolved-thunks'));assert thunks[-1]==0
    names=['MmAllocateContiguousMemoryEx','MmGetPhysicalAddress','NtAllocateVirtualMemory','DiagNtCreateFile','DiagNtWriteFile','DiagNtFlushBuffersFile','DiagNtClose','DiagHalReturnToFirmware','Entry503HalWriteSMBusValue','Entry503KeDelayExecutionThread']
    handlers=dict(zip(names,thunks[:10]));entry['handlers']=handlers
    kernel=None
    anchor=handlers['DiagNtCreateFile']
    for page in range(anchor&~4095,max(0x80000000,(anchor&~4095)-0x100000),-4096):
        head=capture(page,64,'kernel-scan')
        if head[:2]!=b'MZ':continue
        peoff=struct.unpack_from('<I',head,60)[0]
        if not 64<=peoff<=4096:continue
        header=capture(page,8192,'kernel-header')
        if header[peoff:peoff+4]!=b'PE\0\0':continue
        optional=peoff+24
        assert struct.unpack_from('<H',header,optional)[0]==0x10b
        size=struct.unpack_from('<I',header,optional+56)[0]
        if not all(page<=h<page+size for h in handlers.values()):continue
        export_rva,export_size=struct.unpack_from('<II',header,optional+96)
        assert 0<export_rva<size and 40<=export_size<=size-export_rva
        exports=capture(page+export_rva,40,'kernel-exports')
        base,count=struct.unpack_from('<II',exports,16);functions=struct.unpack_from('<I',exports,28)[0]
        assert 0<count<=1024 and 0<functions<=size-count*4
        addresses=struct.unpack('<'+'I'*count,capture(page+functions,count*4,'kernel-export-functions'))
        for name,ordinal in zip(names,[166,173,184,190,236,198,187,49,50,99]):
            assert base<=ordinal<base+count
            offset=addresses[ordinal-base]
            assert 0<offset<size and not export_rva<=offset<export_rva+export_size
            assert page+offset==handlers[name]
            capture(handlers[name],32,'kernel-'+name)
        kernel=dict(base=page,size=size,timestamp=struct.unpack_from('<I',header,peoff+8)[0],export_base=base,export_count=count)
        break
    assert kernel is not None,'bounded kernel identity not found'
    entry['kernel']=kernel
    entry['translations']={}
    for label,address in [('code',sym['entry498_gate']),('data',sym['entry498_record']),('stack',entry['registers']['ESP']),('create',anchor)]:
        pa=translate(address,entry['registers'],label)
        assert pa<0x4000000
        assert capture(address,16,label+'-virtual')==capture(pa,16,label+'-physical',True)
        entry['translations'][label]=dict(virtual=address,physical=pa)
    for table in ('GDT','IDT'):
        match=re.search(table+r'\s*=\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',entry['raw_registers'])
        assert match,table
        address,limit=(int(x,16) for x in match.groups())
        assert 0<limit<8192 and address+limit<2**32
        capture(address,limit+1,table.lower())
    save()
    from indicator_calls import transaction
    result=transaction(ActualCalls(handlers),sym,xbe,calls)
    r['actual_kernel_calls']=result['files'];r['indicator_calls']=result
    r.update(actual_completed_kernel_calls=12,original_start_not_executed=True,
             windows_started=False,normal_guest_shutdown=False,physical_qualification=False,
             final_flush_and_close_observed=True,registers_and_flags_restored=True)
    # All observation breakpoints are removed before allowing firmware return.
    for point in list(active):bp(point,False)
    assert g.ask('qqemu.PhyMemMode')=='0'
    r['physical_mode_restored']=True
    g.send('c');stopped=False
    g.s.close();g=None
    r['firmware_execution_resumed_utc']=utc();save()
    from waiter import wait_control
    r['dashboard_observations']=[]
    def dashboard_record(row):
        row['utc']=utc();r['dashboard_observations'].append(row);save()
    r['dashboard_control']=wait_control(6136,credentials,'/E/Applications/XWNBoot510a/entry.bin',dashboard_record)
    r['dashboard_return_observed']=True
    r['live_ftp_receipt_readback']=False
    r['cold_receipt_verification_required']=True
    r['passed']=True;save()

except BaseException as e:
    r['error']=repr(e);save();raise
finally:
    try:
        if g:
            if not stopped:
                mon('stop');stopped=True;g.ask('?')
            if physical_mode:
                assert g.ask('Qqemu.PhyMemMode:0')=='OK';physical_mode=False
            for point in list(active):bp(point,False)
            r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0'
            r['asynchronous_stop_replies']=getattr(g,'async_stops',[])
            g.s.close()
    except BaseException as e:r['cleanup_error']=repr(e)
    r.update(ended_utc=utc(),remaining_breakpoints=sorted(active),physical_mode_remaining=physical_mode)
    save()
    if RUN.exists():(RUN/'capture-complete.signal').touch(exist_ok=False)
