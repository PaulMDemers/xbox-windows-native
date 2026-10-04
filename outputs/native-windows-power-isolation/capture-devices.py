"""Read-only NT5 driver/device power inventory in one explicitly owned emulator."""
import argparse, json, pathlib, re, struct, sys
out = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(out.parent / 'native-windows-prebuild'))
from monitor_capture import command, acquire_monitor_lock
p = argparse.ArgumentParser()
p.add_argument('--port', required=True, type=int)
p.add_argument('--state', required=True, type=pathlib.Path)
p.add_argument('--output', required=True, type=pathlib.Path)
a = p.parse_args()
state = json.loads(a.state.read_text())
modules = {int(m['base'], 16): m['name'] for m in state['modules']}
raw = a.output.with_suffix('.ram')
assert not raw.exists()
r = {'scope': 'Read-only emulator RAM and I/O-register observation; no live code patches',
     'drivers': [], 'source_state': a.state.name}
with acquire_monitor_lock(a.port):
    running = 'VM status: running' in command(a.port, 'info status')
    command(a.port, 'stop')
    try:
        regs = command(a.port, 'info registers')
        cr3 = int(re.search(r'CR3=([0-9a-fA-F]+)', regs)[1], 16)
        command(a.port, 'pmemsave 0 67108864 ' + json.dumps(raw.resolve().as_posix()))
        data = raw.read_bytes()
        assert len(data) == 64 * 1024**2
        def phys32(at):
            return struct.unpack_from('<I', data, at)[0]
        def pa(va):
            pde = phys32((cr3 & 0xfffff000) + 4 * (va >> 22))
            assert pde & 1
            if pde & 128:
                return (pde & 0xffc00000) + (va & 0x3fffff)
            pte = phys32((pde & 0xfffff000) + 4 * ((va >> 12) & 1023))
            assert pte & 1
            return (pte & 0xfffff000) + (va & 4095)
        def read(va, size):
            b = b''
            while size:
                n = min(size, 4096 - (va & 4095))
                at = pa(va)
                assert at + n <= len(data)
                b += data[at:at+n]
                va += n
                size -= n
            return b
        def u32(va):
            return struct.unpack('<I', read(va, 4))[0]
        def string(va):
            size, maximum, buffer = struct.unpack('<HHI', read(va, 8))
            assert size <= maximum and size < 2048
            return read(buffer, size).decode('utf-16le') if size else ''
        # The exact native PDB supplies these structure sizes/offsets. Verify
        # the driver through its first device's back-pointer before recording it.
        seen = set()
        for match in re.finditer(b'\x04\x00\xa8\x00', data):
            at = match.start()
            if at % 4 or at + 168 > len(data):
                continue
            base = phys32(at + 12)
            if base not in modules:
                continue
            device = phys32(at + 4)
            if not device:
                continue
            try:
                driver = u32(device + 8)
                if pa(driver) != at or driver in seen:
                    continue
                seen.add(driver)
                item = {'address': hex(driver), 'name': string(driver + 28),
                        'module': modules[base], 'base': hex(base),
                        'power_dispatch': hex(u32(driver + 56 + 22 * 4)),
                        'devices': []}
                visited = set()
                while device:
                    assert device not in visited and len(visited) < 128
                    visited.add(device)
                    assert u32(device + 8) == driver
                    d = {'address': hex(device), 'flags': hex(u32(device + 28)),
                         'attached': hex(u32(device + 16)), 'current_irp': hex(u32(device + 20)),
                         'extension': hex(u32(device + 40)),
                         'queue_busy': read(device + 112, 1)[0],
                         'queue_links': [hex(u32(device + off)) for off in (100, 104)]}
                    ext = u32(device + 176)
                    if ext:
                        assert u32(ext + 4) == device
                        d['power_flags'] = hex(u32(ext + 8))
                        d['extension_flags'] = hex(u32(ext + 16))
                        dn = u32(ext + 20)
                        if dn:
                            d['instance'] = string(dn + 64)
                            d['capability_flags'] = hex(u32(dn + 160))
                        power = u32(ext + 12)
                        if power:
                            d['power_state'] = u32(power + 28)
                            d['power_extension'] = read(power, 80).hex()
                    item['devices'].append(d)
                    device = u32(device + 12)
                r['drivers'].append(item)
            except (AssertionError, struct.error, UnicodeError) as ex:
                r.setdefault('candidate_errors', []).append({'physical': hex(at), 'error': repr(ex)})
        for cmd in ['info pic', 'info irq', 'i /1bx 0x3f6', 'i /1bx 0xff60', 'i /1bx 0xff62']:
            r[cmd] = command(a.port, cmd)
    finally:
        if running:
            command(a.port, 'cont')
        raw.unlink(missing_ok=True)
        r['raw_memory_removed'] = not raw.exists()
a.output.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({'drivers': len(r['drivers']), 'output': str(a.output)}))
