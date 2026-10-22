"""Fresh diskless execution of the pinned i386 backend, independent Python bus.

No port I/O, physical disk, VM image or historical runtime is opened.
"""
import datetime
import hashlib
import json
import struct
import sys
from pathlib import Path

K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(W / 'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x

B = Path('C:/xwn653/host001')
H = json.loads((K / 'host001.json').read_text())
assert H['status'] == 'passed'
for name, pin in H['artifacts'].items():
    assert hashlib.sha256((B / name).read_bytes()).hexdigest() == pin['sha256']
for name, sha in H['source_pins'].items():
    assert hashlib.sha256((K / name).read_bytes()).hexdigest() == sha
symbols = {a[2]: int(a[0], 16) for line in (B / 'symbols.stdout').read_text().splitlines()
           if len(a := line.split()) == 3}
blob = (B / 'pio.bin').read_bytes()
assert len(blob) < 0x8000
out = K / 'compiled001.json'
assert not out.exists()
report = dict(passed=False, physical_access=False, cases=[],
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              binary_sha256=H['artifacts']['pio.bin']['sha256'],
              scope='Exact linked i386 backend with independent modeled callbacks; no hardware proof')


def save():
    out.write_text(json.dumps(report, indent=2) + '\n')


class Machine:
    def __init__(self, fault='', at=0):
        self.fault, self.at = fault, at
        self.cpu = u.Uc(u.UC_ARCH_X86, u.UC_MODE_32)
        for address in (0x100000, 0x200000, 0x300000):
            self.cpu.mem_map(address, 0x10000)
        self.cpu.mem_write(0x100000, blob)
        self.ctx, self.io, self.plan, self.expected, self.buffer = (
            0x200000, 0x200100, 0x200200, 0x200300, 0x201000)
        self.stub, self.end, self.stack = 0x108000, 0x109000, 0x30f000
        self.ident = bytearray(512)
        for word, value in ((0, 0x40), (49, 0x200), (83, 0x5000),
                            (60, 100000 & 65535), (61, 100000 >> 16)):
            struct.pack_into('<H', self.ident, word * 2, value)
        expected = bytearray(self.ident)
        if fault == 'identity':
            expected[20] ^= 1
        self.cpu.mem_write(self.expected, bytes(expected))
        self.cpu.mem_write(self.io, struct.pack('<7I', 0x76543210,
                           *(self.stub + i * 16 for i in range(6))))
        plan = [100000, 1000, 10000, 1100, 1200, 1300, 1400, 8,
                0 if fault == 'policy' else 1]
        if fault == 'alias':
            plan[5] = plan[4]
        self.cpu.mem_write(self.plan, struct.pack('<9I', *plan))
        self.task = {}
        self.commands = []
        self.calls = self.acks = self.words = self.writes = 0
        self.position = 256
        self.cmd = 0
        self.sector = 0
        self.disk = {lba: bytearray((i + lba) % 256 for i in range(512))
                     for lba in (1200, 1300, 1400)}
        self.cache = {lba: bytearray(b) for lba, b in self.disk.items()}
        self.failed_call = None
        self.cpu.hook_add(u.UC_HOOK_CODE, self.callback,
                          begin=self.stub, end=self.stub + 5 * 16)

    def invoke(self, name, *args):
        cpu = self.cpu
        cpu.mem_write(self.stack, struct.pack('<' + 'I' * (1 + len(args)), self.end, *args))
        cpu.reg_write(x.UC_X86_REG_ESP, self.stack)
        cpu.reg_write(x.UC_X86_REG_EFLAGS, 2)
        registers = (x.UC_X86_REG_EBX, x.UC_X86_REG_ESI, x.UC_X86_REG_EDI, x.UC_X86_REG_EBP)
        for reg in registers:
            cpu.reg_write(reg, 0x12345678)
        cpu.emu_start(symbols[name], self.end, count=2000000)
        assert cpu.reg_read(x.UC_X86_REG_EIP) == self.end, 'instruction bound'
        assert cpu.reg_read(x.UC_X86_REG_ESP) == self.stack + 4
        assert all(cpu.reg_read(reg) == 0x12345678 for reg in registers)
        assert not (cpu.reg_read(x.UC_X86_REG_EFLAGS) & 0x200)
        return cpu.reg_read(x.UC_X86_REG_EAX)

    def callback(self, cpu, address, size, unused):
        which = (address - self.stub) // 16
        assert address == self.stub + which * 16 and which in range(6)
        sp = cpu.reg_read(x.UC_X86_REG_ESP)
        dest, opaque, reg, arg = struct.unpack('<4I', cpu.mem_read(sp, 16))
        assert opaque == 0x76543210
        self.calls += 1
        # Fail before/after an observable callback. flags has no error return.
        error = which != 5 and self.fault in ('io_before', 'io_after') and self.calls == self.at
        result = 0
        if not error or self.fault == 'io_after':
            result = self.operation(which, reg, arg)
        if error:
            result = 1
            self.failed_call = self.calls
        cpu.reg_write(x.UC_X86_REG_EAX, result)
        cpu.reg_write(x.UC_X86_REG_ESP, sp + 4)
        cpu.reg_write(x.UC_X86_REG_EIP, dest)

    def operation(self, which, reg, arg):
        active_fault = len(self.commands) == self.at and bool(self.at)
        if which == 5:
            return 0x200 if self.fault == 'if' else 0
        if which == 4:
            return 0  # Model only: does NOT establish a real 400 ns delay.
        if which == 0:
            assert reg in (6, 7, 8, 9)
            if reg == 8:
                value = int(self.fault == 'dma' and active_fault)
            elif reg == 9:
                value = 4 if self.fault == 'pending' else 0
            else:
                value = 0x48 if self.position < 256 else 0x40
                if active_fault:
                    value = {'busy': 0xa1, 'no_drq': 0x40, 'error': 0x41,
                             'floating': 0xff, 'zero': 0}.get(self.fault, value)
                    if self.fault == 'ack_mismatch' and reg == 6:
                        value = 0x80
                if reg == 6:
                    self.acks += 1
            self.cpu.mem_write(arg, bytes([value]))
        elif which == 2:
            assert reg in (1, 2, 3, 4, 5, 6)
            self.task[reg] = arg & 255
            if reg == 6:
                self.cmd = arg
                assert arg in (0xec, 0x20, 0x30, 0xe7)
                self.commands.append(arg)
                if arg in (0x20, 0x30):
                    assert self.task[1] == 1
                    self.sector = (self.task[2] | self.task[3] << 8 |
                                   self.task[4] << 16 | (self.task[5] & 15) << 24)
                    assert self.sector in self.cache, 'foreign LBA'
                self.position = 256 if arg == 0xe7 else 0
                if arg == 0xe7:
                    self.disk = {lba: bytearray(b) for lba, b in self.cache.items()}
        else:
            assert which in (1, 3) and reg == 0 and self.position < 256
            if which == 1:
                assert self.cmd in (0xec, 0x20)
                data = self.ident if self.cmd == 0xec else self.cache[self.sector]
                self.cpu.mem_write(arg, bytes(data[self.position * 2:self.position * 2 + 2]))
            else:
                assert self.cmd == 0x30
                struct.pack_into('<H', self.cache[self.sector], self.position * 2, arg & 65535)
                self.writes += 1
            self.position += 1
            self.words += 1
        return 0


def run(fault='', at=0):
    m = Machine(fault, at)
    result = m.invoke('admit653', m.ctx, m.io, m.plan, m.expected)
    original = {lba: bytes(b) for lba, b in m.cache.items()}
    desired = {lba: bytes((i * 7 + lba) % 256 for i in range(512)) for lba in original}
    sequence = [('read653', 0), ('read653', 1), ('read653', 2),
                ('write653', 0), ('write653', 1), ('flush653', None),
                ('read653', 0), ('read653', 1), ('write653', 2),
                ('flush653', None), ('read653', 0), ('read653', 1), ('read653', 2)]
    completed = 0
    if not result:
        for name, slot in sequence:
            if fault == 'order':
                name, slot = 'write653', 0
            if name == 'write653':
                m.cpu.mem_write(m.buffer, desired[1200 + slot * 100])
            args = (m.ctx,) if slot is None else (m.ctx, slot, m.buffer)
            result = m.invoke(name, *args)
            if result:
                break
            if name == 'read653':
                reference = original if completed < 3 else desired
                assert bytes(m.cpu.mem_read(m.buffer, 512)) == reference[1200 + slot * 100]
            completed += 1
    assert bool(result) == bool(fault), (fault, at, result, completed)
    if not fault:
        assert m.disk == desired and m.words == 3072 and m.writes == 768 and m.acks == 26
        assert m.commands == [0xec, 0x20, 0x20, 0x20, 0x30, 0x30, 0xe7,
                              0x20, 0x20, 0x30, 0xe7, 0x20, 0x20, 0x20]
    if fault in ('policy', 'alias'):
        assert m.calls == 0
    if fault in ('if', 'pending'):
        assert not m.commands and not m.acks
    if fault == 'identity':
        assert m.commands == [0xec] and not m.writes
    if fault.startswith('io_'):
        assert m.failed_call == at and m.calls == at
    calls = m.calls
    again = m.invoke('read653', m.ctx, 0, m.buffer)
    assert again and calls == m.calls, 'unexpected retry I/O'
    return dict(fault=fault or 'none', at=at, result=result, completed=completed,
                callbacks=calls, commands=len(m.commands), words=m.words,
                acknowledged_status_reads=m.acks, retry_refused=True)


save()
try:
    cases = [('', 0)] + [(f, 0) for f in ('policy', 'alias', 'if', 'pending', 'identity', 'order')]
    cases += [(f, n) for f in ('busy', 'error', 'floating', 'zero', 'ack_mismatch', 'dma')
              for n in (1, 5, 7, 10, 11, 14)]
    cases += [('no_drq', n) for n in (1, 5, 10, 14)]
    # Known read8 callbacks early in admission; no flags pseudo-error injection.
    cases += [(f, n) for f in ('io_before', 'io_after') for n in (2, 3)]
    for fault, at in cases:
        report['cases'].append(run(fault, at))
        save()
    report['passed'] = True
except BaseException as e:
    report['failure'] = repr(e)
    raise
finally:
    report['ended_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
print(json.dumps(dict(passed=report['passed'], cases=len(report['cases']))))
