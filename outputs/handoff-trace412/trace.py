"""One owned emulator launch; read-only original handoff trace, bounded teardown."""
import ast
import datetime
import ftplib
import hashlib
import json
import re
import struct
import sys
import time
from pathlib import Path
from protocol import Remote, monitor

K = Path(__file__).resolve().parent
W = K.parents[1]
O = K / 'emu001'
RUN = Path('E:/xwn412/runs/nt5-handoff412-emu001')
PRIVATE = Path('E:/xwn412/trace001')
sys.path.insert(0, str(W / 'outputs/surface-bridge260'))
from atomic_json import write_json
assert not (O / 'trace.json').exists() and not PRIVATE.exists()
PRIVATE.mkdir()
prep = json.loads((K / 'preparation002.json').read_text(encoding='utf-8'))
sym = prep['symbols']
xbe = Path('E:/xwn374/build001/default.xbe').read_bytes()
sha = lambda b: hashlib.sha256(b).hexdigest()
assert sha(xbe) == prep['original_xbe_sha256']
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
    reply = monitor(5486, command)
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
    d = {n: int(v, 16) for n, v in re.findall(r'\b(EIP|ESP|ESI|EDX|ECX|EFL|CR0|CR3|CR4)=([0-9a-fA-F]+)', text)}
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
            f.connect('127.0.0.1', 5488, timeout=3)
            f.login(*credentials)
            break
        except ftplib.all_errors:
            f.close()
            assert time.monotonic() < deadline
            time.sleep(.5)
    mon('stop')
    stopped = True
    g = Remote(5487)
    r['initial_stop'] = g.ask('?')
    assert g.ask('qqemu.PhyMemMode') == '0'
    bp(sym['_start'], True)
    g.send('c')
    stopped = False
    r['launch'] = dict(requested_utc=utc(), command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe')
    save()
    try:
        f.sock.settimeout(6)
        r['launch']['reply'] = f.sendcmd(r['launch']['command'])
    except ftplib.all_errors as e:
        r['launch']['reply_uncertain'] = type(e).__name__
    finally:
        f.close()
    save()
    entry = await_stop(sym['_start'], 'original_entry')
    assert capture(0x11100, 0x1f00, 'loaded-original-wrapper') == xbe[0x1100:0x3000]
    assert capture(0x13000, 288316, 'loaded-original-payload') == xbe[0x3000:0x3000+288316]
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
    pre = advance(sym['blentry']-2, 'before_original_indirect_jump')
    reg = pre['registers']
    values = {n: struct.unpack('<I', capture(sym[n], 4, n))[0] for n in
              ('kernelram', 'phys_kernelram', 'bootloaderram', 'phys_bootloaderram', 'ptr_PAGE_SIZE')}
    pre['variables'] = values
    alias = values['phys_bootloaderram']
    assert values['ptr_PAGE_SIZE'] == 4096 and alias == reg['EDX']
    assert reg['ESI'] == values['phys_kernelram']
    assert reg['ECX'] == (alias-sym['blentry']) & 0xffffffff
    source = capture(sym['blentry'], 1024, 'loader-source')
    expected = bytearray(source)
    target = alias+sym['newloc']-sym['blentry']
    struct.pack_into('<I', expected, sym['ptr_newloc']-sym['blentry'], target)
    assert capture(values['bootloaderram'], 1024, 'high-loader') == expected
    assert capture(alias, 1024, 'low-loader') == expected
    pa = translate(alias, reg, 'low-loader')
    high_pa = translate(values['bootloaderram'], reg, 'high-loader')
    pre['low_physical'] = pa
    pre['high_physical'] = high_pa
    assert capture(pa, 1024, 'low-physical', True) == expected
    assert capture(high_pa, 1024, 'high-physical', True) == expected
    assert high_pa == alias
    assert capture(values['kernelram'], 288316, 'allocated-payload') == xbe[0x3000:0x3000+288316]
    save()
    low = advance(alias, 'relocated_entry_paging_on')
    assert low['registers']['CR0'] & 0x80000000
    assert capture(alias, 16, 'relocated-entry-code') == expected[:16]
    off = advance(alias+12, 'immediately_after_paging_disabled')
    assert not off['registers']['CR0'] & 0x80000000
    assert capture(alias+12, 16, 'paging-off-code') == expected[12:28]
    new = advance(target, 'far_jump_new_cs')
    assert not new['registers']['CR0'] & 0x80000000 and new['registers']['CR3'] == 0
    assert capture(target, 12, 'newloc-code') == xbe[sym['newloc']-0x10000:sym['newloc']-0x10000+12]
    # The destination comes from the byte-pinned MOV EDI,imm32 at original newloc.
    code = xbe[sym['newloc']-0x10000:sym['newloc']-0x10000+5]
    assert code[0] == 0xbf
    destination = struct.unpack_from('<I', code, 1)[0]
    cromwell = advance(destination, 'original_cromwell_first_instruction')
    assert not cromwell['registers']['CR0'] & 0x80000000
    assert capture(destination, 288316, 'relocated-cromwell') == xbe[0x3000:0x3000+288316]
    r.update(passed=True, historical_physical_failure_reproduced=False,
             stopped_before_first_cromwell_instruction=True, windows_started=False)
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
            g.s.close()
    except BaseException as e:
        r['cleanup_error'] = repr(e)
    r.update(ended_utc=utc(), remaining_breakpoints=sorted(active), physical_mode_remaining=physical_mode)
    save()
    (RUN / 'capture-complete.signal').touch(exist_ok=False)
