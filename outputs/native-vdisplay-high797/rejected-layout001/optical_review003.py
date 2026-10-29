"""Fresh isolated exact-bridge renderer checks; no hardware or device model.
Direct renderer entry assumes the caller's admitted framebuffer; CPU/integration
fixtures separately verify refused headers and real bridge call sites.
"""
import datetime, hashlib, json, os, random, struct, sys, time
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
P = Path('C:/xwn797/host004')
sys.path.insert(0, str(W / 'work/python-packages'))
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_INSN
from unicorn import x86_const as x
from optical_oracle import paint_report

assert os.environ.get('XBOX_XEMU_MODE') == 'exclusive'
sha = lambda b: hashlib.sha256(b).hexdigest()
out = K / 'optical-review001.json'
assert not out.exists()
h = json.loads((K / 'host004.json').read_text())
assert h['passed']
for n, pin in h['sources'].items():
    assert sha((K / n).read_bytes()) == pin
for n, pin in h['files'].items():
    assert sha((P / n).read_bytes()) == pin
offsets = (0x8d4,0x66b8,0x67d0,0x67f0,0x6d84,0x6dfc,0x6e74,0x6eec,0x6f64,0x6f50,0x6f5c,0x6f60)
r = {'passed': False, 'physical_access': False, 'scope': __doc__,
     'harness_sha256': sha(Path(__file__).read_bytes()), 'cases': []}
deadline = time.monotonic() + 180

def run(label, values, layout):
    assert time.monotonic() < deadline
    page = (P / layout / 'page.bin').read_bytes()
    base = struct.unpack_from('<I', page, 0x844)[0]
    fb, size = 0x3000000, 3686400
    c = Uc(UC_ARCH_X86, UC_MODE_32)
    c.mem_map(base - 4096, 40960)
    c.mem_write(base - 4096, b'G' * 40960)
    c.mem_write(base, page)
    c.mem_map(fb - 4096, size + 8192)
    c.mem_write(fb - 4096, b'Z' * (size + 8192))
    for offset, value in zip(offsets, values):
        c.mem_write(base + offset, struct.pack('<I', value))
    before = bytes(c.mem_read(base, 0x7800))
    regs = [(x.UC_X86_REG_EAX, 0x12345678), (x.UC_X86_REG_EBX, 0x87654321),
            (x.UC_X86_REG_ECX, 0xabcdef01), (x.UC_X86_REG_EDX, 0x10203040),
            (x.UC_X86_REG_ESI, 0x31415926), (x.UC_X86_REG_EDI, 0x27192818),
            (x.UC_X86_REG_EBP, base)]
    for reg, value in regs:
        c.reg_write(reg, value)
    end = base + h['bridge_symbols']['bridge_hold']
    c.reg_write(x.UC_X86_REG_ESP, base + 0x8000 - 4)
    c.mem_write(base + 0x8000 - 4, struct.pack('<I', end))
    c.reg_write(x.UC_X86_REG_EFLAGS, 2)
    def forbidden(*args):
        raise AssertionError('renderer performed device I/O')
    c.hook_add(UC_HOOK_INSN, forbidden, None, 1, 0, x.UC_X86_INS_IN)
    c.hook_add(UC_HOOK_INSN, forbidden, None, 1, 0, x.UC_X86_INS_OUT)
    c.emu_start(base + h['bridge_symbols']['bridge_report'], end,
                timeout=5000000, count=2000000)
    assert c.reg_read(x.UC_X86_REG_EIP) == end
    assert c.reg_read(x.UC_X86_REG_ESP) == base + 0x8000
    assert all(c.reg_read(reg) == value for reg, value in regs)
    assert c.reg_read(x.UC_X86_REG_EFLAGS) & 0x600 == 0
    assert bytes(c.mem_read(base, 0x7800)) == before
    for pointer in (base - 4096, base + 32768):
        assert bytes(c.mem_read(pointer, 4096)) == b'G' * 4096
    for pointer in (fb - 4096, fb + size):
        assert bytes(c.mem_read(pointer, 4096)) == b'Z' * 4096
    expected = bytearray(b'Z' * size)
    words = [0x7970000d] + values
    paint_report(expected, words)
    assert bytes(c.mem_read(fb, size)) == expected, 'full framebuffer mismatch'
    r['cases'].append({'name': label, 'layout': layout, 'words': words,
                       'all_pixels_and_guards_exact': True, 'registers_preserved': True})

try:
    patterns = [('zero', [0] * 12), ('ones', [0xffffffff] * 12),
                ('alternating', [0xaaaaaaaa, 0x55555555] * 6),
                ('distinct', [0x10203040 + i * 0x01010101 for i in range(12)])]
    for bit in range(32):
        hot = [1 << ((bit + i) % 32) for i in range(12)]
        patterns.append(('one-' + str(bit), hot))
        patterns.append(('zero-' + str(bit), [v ^ 0xffffffff for v in hot]))
    rng = random.Random(719)
    for i in range(8):
        patterns.append(('random-' + str(i), [rng.getrandbits(32) for _ in range(12)]))
    for i, (label, values) in enumerate(patterns):
        run(label, values, 'dual' if i % 2 == 0 else 'relocated')
    r['passed'] = True
except BaseException as e:
    r['failure'] = repr(e)
    raise
finally:
    r['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out.write_text(json.dumps(r, indent=2) + '\n')
print('PASS', len(r['cases']), 'whole-framebuffer renderer cases; no hardware proof')
