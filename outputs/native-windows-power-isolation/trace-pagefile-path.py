"""Observe the native pagefile usage-notification call; never alter its result."""
import argparse, ftplib, json, pathlib, struct, sys, time
out = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(out.parent / 'native-windows-physical-bootvideo'), str(out.parent / 'native-windows-prebuild')]
from debug_remote import Remote
from monitor_capture import command, acquire_monitor_lock
p = argparse.ArgumentParser()
p.add_argument('--run', required=True, type=pathlib.Path)
p.add_argument('--kernel-base', type=lambda x:int(x, 0), default=0x82410000)
a = p.parse_args()
K = a.kernel_base
pubs = json.loads((out.parent / 'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
r = {'scope': 'Exploratory read-only execution-breakpoint trace in xemu; no patched results', 'events': []}
def u(g, at): return struct.unpack('<I', g.read(at, 4))[0]
def string(g, at):
    n, m, b = struct.unpack('<HHI', g.read(at, 8))
    assert n <= m and n < 512
    return g.read(b, n).decode('utf-16le') if n else ''
active = set()
# Wait only for this run's explicitly forwarded dashboard server.
deadline = time.monotonic() + 45
while True:
    try:
        with ftplib.FTP() as ready:
            ready.connect('127.0.0.1', 4596, timeout=2)
            ready.login('xbox', 'xbox')
        break
    except ftplib.all_errors:
        assert time.monotonic() < deadline, 'Private dashboard FTP unavailable'
        time.sleep(1)
with acquire_monitor_lock(4594):
    command(4594, 'stop')
    g = Remote(4595)
    g.s.settimeout(40)
    g.ask('qSupported'); g.ask('?')
    def bp(at): g.bp(at); active.add(at)
    def remove(at): g.bp(at, False); active.remove(at)
    try:
        entry = K + pubs['_MiCheckPageFilePath@4']['rva']
        bp(entry); g.send('c')
        with ftplib.FTP() as ftp:
            ftp.connect('127.0.0.1', 4596, timeout=15); ftp.login('xbox', 'xbox')
            r['launch'] = ftp.sendcmd(r'SITE EXEC E:\Apps\XWN\default.xbe')
        for _ in range(128):
            g.recv(); regs = g.regs(); assert regs['eip'] == entry
            filename = string(g, u(g, regs['esp'] + 4) + 48)
            if filename.lower().endswith('\\pagefile.sys'):
                break
            r.setdefault('other_path_checks', []).append(filename)
            remove(entry); g.send('s'); g.recv(); bp(entry); g.send('c')
        else:
            raise RuntimeError('Pagefile path not observed within entry bound')
        ret = u(g, regs['esp']); expected_sp = regs['esp'] + 8
        fo = u(g, regs['esp'] + 4)
        r['file_object'] = hex(fo); r['file_name'] = string(g, fo + 48)
        head = K + pubs['_PsLoadedModuleList']['rva']; link = u(g, head); driver = 0
        for _ in range(256):
            if link == head: break
            if string(g, link + 44).lower() == 'xwnfatx.sys': driver = u(g, link + 24)
            link = u(g, link)
        assert driver
        pnp = driver + 0x10820  #0054 VfatPnp, validated by build symbols
        call = K + pubs['@IopfCallDriver@8']['rva']
        pending = []; target_irp = 0
        remove(entry); bp(pnp); bp(ret); g.send('c')
        for _ in range(300):
            g.recv(); regs = g.regs()
            if regs['eip'] == ret and regs['esp'] == expected_sp:
                r['native_return_status'] = hex(regs['eax']); break
            assert regs['eip'] in active
            if regs['eip'] == pnp:
                ctx = u(g, regs['esp'] + 4); irp = u(g, ctx); stack = u(g, ctx + 32)
                target_irp = irp
                if call not in active: bp(call)
                r['events'].append({'event': 'VfatPnp', 'irp': hex(irp), 'context': hex(ctx),
                    'major_minor': g.read(stack, 2).hex(), 'parameters': g.read(stack + 4, 16).hex(),
                    'storage_device': hex(u(g, u(g, ctx + 8) + 136))})
            elif regs['eip'] == call:
                irp = regs['edx']; stack = u(g, irp + 96) - 36
                # Storage drivers may create a fresh usage IRP for their parent.
                # Include those descendants, not only the original IRP pointer.
                if g.read(stack, 2) == b'\x1b\x16':
                    dev = regs['ecx']; obj = u(g, dev + 8); back = u(g, regs['esp'])
                    event = {'event': 'LowerCall', 'device': hex(dev), 'driver': string(g, obj + 28),
                             'irp': hex(irp), 'original_irp': irp == target_irp,
                             'parameters': g.read(stack + 4, 16).hex(),
                             'pnp_dispatch': hex(u(g, obj + 56 + 27 * 4)), 'return_address': hex(back)}
                    r['events'].append(event)
                    pending.append((back, regs['esp'] + 4, event))
                    if back not in active: bp(back)
            else:
                for frame in list(pending):
                    back, sp, event = frame
                    if regs['eip'] == back and regs['esp'] == sp:
                        event['native_return_status'] = hex(regs['eax'])
                        pending.remove(frame)
            at = regs['eip']; remove(at); g.send('s'); g.recv(); bp(at); g.send('c')
        else: raise RuntimeError('Pagefile path did not return within event bound')
    except Exception as ex:
        r['error'] = repr(ex)
        g.s.sendall(b'\x03')
        try: g.recv()
        except Exception: pass
    finally:
        for at in list(active):
            try: remove(at)
            except Exception: pass
        g.s.close()
        command(4594, 'cont')
        (a.run / 'pagefile-path-trace.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
