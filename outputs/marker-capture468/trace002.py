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
from marker_decode import success
from refusal_decode002 import decode_refusal

K = Path(__file__).resolve().parent
W = K.parents[1]
O = K / 'emu002'
RUN = Path('C:/xwn468/runs/nt5-capture468-emu002')
PRIVATE = Path('C:/xwn468/trace002')
sys.path.insert(0, str(W / 'outputs/surface-bridge260'))
from atomic_json import write_json
assert not (O / 'trace.json').exists() and not PRIVATE.exists()
PRIVATE.mkdir()
build=json.loads((K/'build001.json').read_text())
sym=build['wrapper_symbols'];stub=build['stub_symbols']
review=json.loads((K/'source-review001.json').read_text());assert review['passed']
xbe=Path('C:/xwn468/build001/default.xbe').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(xbe)==build['sha256']
payload=xbe[0x3000:0x3000+build['payload_bytes']]
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
    reply = monitor(5684, command)
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


save()
try:
    deadline = time.monotonic()+65
    while not (RUN / 'startup-ready.json').exists():
        assert time.monotonic() < deadline and not (RUN / 'cleanup.json').exists()
        time.sleep(.25)
    tree = ast.parse((W / 'outputs/native-windows-prebuild/launch_unleashx.py').read_text(encoding='utf-8'))
    login = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'login')
    credentials = [ast.literal_eval(arg) for arg in login.args]
    while True:
        f = ftplib.FTP()
        try:
            f.connect('127.0.0.1', 5686, timeout=3)
            f.login(*credentials)
            break
        except ftplib.all_errors:
            f.close()
            assert time.monotonic() < deadline
            time.sleep(.5)
    prepared=json.loads((K/'preparation001.json').read_text());assert prepared['status']=='prepared'
    r['stage']={'directory':'E:/Applications/XWNBoot468a','offline_prepared':True,'readback_sha256':prepared['change']['sha256']}
    assert r['stage']['readback_sha256']==sha(xbe);save()
    mon('stop')
    stopped = True
    g = Remote(5685)
    r['initial_stop'] = g.ask('?')
    assert g.ask('qqemu.PhyMemMode') == '0'
    bp(sym['_start'], True)
    g.send('c')
    stopped = False
    r['launch'] = dict(requested_utc=utc(), command=r'SITE EXEC E:\Applications\XWNBoot468a\default.xbe')
    save()
    try:
        f.sock.settimeout(6)
        r['launch']['reply'] = f.sendcmd(r['launch']['command'])
    except ftplib.all_errors as e:
        r['launch']['reply_uncertain'] = type(e).__name__
    finally:
        f.close()
    save()
    entry = await_stop(sym['_start'], 'diagnostic_entry')
    assert capture(0x11100, 0x1f00, 'loaded-diagnostic-wrapper') == xbe[0x1100:0x3000]
    assert capture(0x13000, len(payload), 'loaded-diagnostic-payload') == payload
    # Capture actual Xbox kernel header and trap pointers; this is not a full
    # symbol-matched kernel pin. Firmware and emulator hashes are pinned separately.
    idt = re.search(r'IDT\s*=\s*([0-9a-fA-F]+)', entry['raw_registers'])
    assert idt
    idt_base = int(idt.group(1), 16)
    gates = [capture(idt_base+i*8, 8, f'idt-vector{i}') for i in (0, 14)]
    handlers = [(struct.unpack_from('<H', b)[0] | (struct.unpack_from('<H', b, 6)[0] << 16)) for b in gates]
    entry['idt_handlers'] = handlers
    kernel_found = False
    for page in range(handlers[0] & ~4095, max(0x80000000, (handlers[0] & ~4095)-0x100000), -4096):
        head = g.read(page, 64)
        if head[:2] != b'MZ':
            continue
        peoff = struct.unpack_from('<I', head, 60)[0]
        if not 64 <= peoff <= 4096:
            continue
        header = capture(page, 8192, 'kernel-header')
        if header[peoff:peoff+4] != b'PE\0\0':
            continue
        size = struct.unpack_from('<I', header, peoff+24+56)[0]
        if all(page <= h < page+size for h in handlers):
            entry['kernel'] = dict(base=page, size=size, timestamp=struct.unpack_from('<I', header, peoff+8)[0])
            for i, handler in enumerate(handlers):
                capture(handler, 32, f'kernel-handler{i}')
            kernel_found = True
            break
    assert kernel_found, 'No bounded resident kernel identity'
    save()
    # Watch both success and refusal without retrying either marker.
    advance(sym['diag_handoff'],'before_first_marker')
    bp(sym['diag_reboot'],True)
    bp(sym['diag_marker_ready'],True)
    stopped=False;g.send('c');reply=g.recv(35);stopped=True
    first=registers('first_marker_terminal');assert reply.startswith(('T','S'))
    raw=capture(sym['before_marker_record'],96,'first-marker-record')
    r['first_marker_raw_words']=list(struct.unpack('<24I',raw));save()
    assert first['registers']['EIP']==sym['diag_marker_ready'],'first marker refused'
    r['first_marker']=success(raw,1)
    bp(sym['diag_reboot'],False);bp(sym['diag_marker_ready'],False)
    # Explicit intervention: model a first-transaction completion error. This
    # exercises actual refusal serialization, never qualifies physical status.
    injected=struct.pack('<24I',0x354b524d,1,96,1,0xff,5,0,1,0x20,2,1000,0,1200,0,0,0,0x20,0,0,4,0,3,1,0)
    r['intervention']=dict(kind='debugger writes modeled marker and refusal entry registers',
       hardware_status_naturally_observed=False,bytes=injected.hex())
    r['guest_memory_or_register_writes']=True;save()
    assert g.ask(f"M{sym['before_marker_record']:x},60:"+injected.hex())=='OK'
    regs=bytearray.fromhex(g.ask('g'))
    struct.pack_into('<I',regs,0,5)
    struct.pack_into('<I',regs,32,sym['diag_reboot'])
    assert g.ask('G'+regs.hex())=='OK'
    advance(sym['refusal_snapshot_ready'],'snapshot_before_cleanup')
    snap=capture(sym['refusal_record'],192,'refusal-snapshot')
    assert snap[80:176]==injected
    r['snapshot_decoded']=decode_refusal(snap)
    advance(sym['refusal_reboot'],'after_fallback_close_before_reboot')
    final=capture(sym['refusal_record'],192,'refusal-after-file-calls')
    assert final==snap
    assert capture(sym['before_marker_record'],96,'live-marker-after-file-calls')==injected
    r.update(passed=True,historical_physical_failure_reproduced=False,
             stopped_before_boot_device=True,windows_started=False,
             actual_emulator_markers=1,actual_loader_executed=False,
             injected_refusal=True,immutable_snapshot=True)
    save()
except BaseException as e:
    r['error'] = repr(e)
    save()
    raise
finally:
    try:
        if g:
            if not stopped:
                mon('stop')
                stopped = True
                g.ask('?')
            if physical_mode:
                assert g.ask('Qqemu.PhyMemMode:0') == 'OK'
                physical_mode = False
            for point in list(active):
                bp(point, False)
            r['physical_mode_restored'] = g.ask('qqemu.PhyMemMode') == '0'
            r['asynchronous_stop_replies']=getattr(g,'async_stops',[])
            g.s.close()
    except BaseException as e:
        r['cleanup_error'] = repr(e)
    r.update(ended_utc=utc(), remaining_breakpoints=sorted(active), physical_mode_remaining=physical_mode)
    save()
    (RUN / 'capture-complete.signal').touch(exist_ok=False)
