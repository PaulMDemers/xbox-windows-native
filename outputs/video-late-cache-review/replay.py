"""Actual NT5 instruction replay with modeled helpers, not a guest cache transition."""
import hashlib
import json
import struct
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
WS = KIT.parents[1]
sys.path.insert(0, str(WS / 'work/python-packages'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EIP, UC_X86_REG_ESP

STACK, STOP, MDL, PT = 0x10000000, 0x11000000, 0x12000000, 0xc03e0000
VA, PA, TAG = 0xf8000000, 0x03c00000, 0x6e775846


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


class Replay:
    def __init__(self, base, image, pages, wc_ready, reserve_failure=False):
        self.base, self.pages = base, pages
        self.calls, self.bugcheck = [], None
        self.u = u = Uc(UC_ARCH_X86, UC_MODE_32)
        u.mem_map(base, (len(image) + 4095) & ~4095)
        u.mem_write(base, image)
        for address, size in [(STACK, 0x10000), (STOP, 4096), (MDL, 8192), (PT-4096, 12288)]:
            u.mem_map(address, size)
        u.mem_write(base+0x73cfc, struct.pack('<I', 0x400))
        u.mem_write(base+0x73d50, bytes([wc_ready]))
        u.mem_write(base+0x72eb0, struct.pack('<I', 0x163))
        u.mem_write(base+0x73d44, bytes(4))
        u.mem_write(PT-8, struct.pack('<II', (pages+2)*2, TAG & ~1))
        u.mem_write(PT-12, b'LEFT')
        u.mem_write(PT+pages*4, b'RGHT')
        u.mem_write(MDL, struct.pack('<IHHIIIII', 0, 28+pages*4, 2, 0, 0, 0x20000000, pages*4096, 0))
        u.mem_write(MDL+28, struct.pack('<'+'I'*pages, *[PA//4096+i for i in range(pages)]))
        self.helpers = {
            base+0x6c1c0: ('MiReserveSystemPtes', 20, 0 if reserve_failure else PT),
            base+0x6c6b0: ('MiReleaseSystemPtes', 12, 0),
            base+0x69098: ('KeFlushCurrentTb', 0, 0),
            base+0x63d14: ('KeInvalidateAllCaches', 4, 1),
        }
        u.hook_add(UC_HOOK_CODE, self.hook)

    def hook(self, u, address, size, user):
        if address == self.base+0x2ac4e:
            esp = u.reg_read(UC_X86_REG_ESP)
            self.bugcheck = list(struct.unpack('<5I', u.mem_read(esp+4, 20)))
            u.emu_stop()
            return
        if address not in self.helpers:
            return
        name, n, result = self.helpers[address]
        esp = u.reg_read(UC_X86_REG_ESP)
        frame = struct.unpack('<'+'I'*(n//4+1), u.mem_read(esp, n+4))
        args = list(frame[1:])
        self.calls.append(dict(name=name, rva=address-self.base, arguments=args, modeled=True))
        if name == 'MiReserveSystemPtes':
            assert args == [self.pages, 0, 0, 0, 0]
        elif name == 'MiReleaseSystemPtes':
            assert args == [PT, self.pages, 0]
        elif name == 'KeInvalidateAllCaches':
            assert args == [1]
        u.reg_write(UC_X86_REG_EAX, result)
        u.reg_write(UC_X86_REG_ESP, esp+n+4)
        u.reg_write(UC_X86_REG_EIP, frame[0])

    def run(self, rva, args, expect_bugcheck=False):
        esp = STACK+0xf000
        self.bugcheck = None
        self.u.mem_write(esp, struct.pack('<'+'I'*(len(args)+1), STOP, *args))
        self.u.reg_write(UC_X86_REG_ESP, esp)
        self.u.emu_start(self.base+rva, STOP, count=200000)
        if expect_bugcheck:
            assert self.bugcheck is not None, 'Expected occupied-PTE rejection'
        else:
            assert self.bugcheck is None
            assert self.u.reg_read(UC_X86_REG_EIP) == STOP, 'Instruction bound exhausted'
            assert self.u.reg_read(UC_X86_REG_ESP) == esp+4*(len(args)+1)
        assert bytes(self.u.mem_read(PT-12, 4)) == b'LEFT'
        assert bytes(self.u.mem_read(PT+self.pages*4, 4)) == b'RGHT'
        return self.u.reg_read(UC_X86_REG_EAX)

    def entries(self):
        return list(struct.unpack('<'+'I'*self.pages, self.u.mem_read(PT, self.pages*4)))

    def expected(self, flags):
        return [PA+i*4096+flags for i in range(self.pages)]


def main():
    dest = KIT/'replay.json'
    assert not dest.exists(), 'Do not overwrite evidence'
    inv = read(KIT/'inventory.json')
    binary = Path(inv['kernel_path'])
    assert sha(binary) == inv['kernel_sha256']
    base = inv['kernel_base']
    pe = pefile.PE(str(binary))
    pe.relocate_image(base)
    image = pe.get_memory_mapped_image()
    for name in ['_MmMapIoSpace@16', '_MmMapLockedPagesWithReservedMapping@16', '_MmUnmapReservedMapping@12']:
        f = inv['functions'][name]
        assert f['resident_matches_disk']
        assert hashlib.sha256(image[f['rva']:f['end_rva']]).hexdigest() == f['resident_sha256']
    io_cases = []
    # Repeat the earlier four mapping cases with corrected helper identities,
    # then independently exercise reservation failure before PTE publication.
    for ready, cache, fail in [(0,0,False),(0,2,False),(1,0,False),(1,2,False),(0,0,True),(1,0,True),(1,2,True)]:
        r = Replay(base, image, 1024, ready, fail)
        result = r.run(0x37d78, [PA,0,0x400000,cache])
        rejected = fail or (ready == 0 and cache == 2)
        names = [c['name'] for c in r.calls]
        if rejected:
            assert result == 0 and not any(r.entries())
            assert names == (['MiReserveSystemPtes'] if fail else ['MiReserveSystemPtes','MiReleaseSystemPtes'])
        else:
            assert result == VA and r.entries() == r.expected(0x17b if cache == 0 else 0x16b)
            assert names == (['MiReserveSystemPtes'] if cache == 0 else ['MiReserveSystemPtes','KeFlushCurrentTb','KeInvalidateAllCaches'])
        io_cases.append(dict(wc_ready=ready, cache=cache, reserve_failure=fail, returned=result,
            first_pte=r.entries()[0], last_pte=r.entries()[-1], modeled_helpers=r.calls))
    reserved_cases = []
    for pages in [1,14,15,1024]:
        for cache in [0,2]:
            r = Replay(base,image,pages,1)
            result = r.run(0x37884,[VA,TAG,MDL,cache])
            initial = r.entries()
            assert result == VA and initial == r.expected(0x17b if cache == 0 else 0x16b)
            # The actual function rejects a live mapping; it is not an in-place
            # cache update API. Trap the genuine bugcheck call in this model.
            r.run(0x37884,[VA,TAG,MDL,2 if cache == 0 else 0],True)
            rejection = r.bugcheck
            assert rejection == [0xda,0x107,VA,PT,PT+pages*4]
            assert r.entries() == initial
            r.run(0x379da,[VA,TAG,MDL])
            gap = r.entries()
            # One-page unmap uses MmKernelDemandZeroPte; all tested PTEs must
            # be nonpresent, not necessarily all-bits-zero on every kernel.
            assert all(not (pte & 1) for pte in gap)
            assert not (struct.unpack('<H',r.u.mem_read(MDL+6,2))[0] & 0x21)
            changed_cache = 2 if cache == 0 else 0
            assert r.run(0x37884,[VA,TAG,MDL,changed_cache]) == VA
            assert r.entries() == r.expected(0x16b if changed_cache == 2 else 0x17b)
            # A bounded restoration can remap the old cache type, but it has a
            # second inaccessible interval. It cannot repair crash safety.
            r.run(0x379da,[VA,TAG,MDL])
            assert all(not (pte & 1) for pte in r.entries())
            assert r.run(0x37884,[VA,TAG,MDL,cache]) == VA and r.entries() == initial
            reserved_cases.append(dict(pages=pages, initial_cache=cache, returned=result,
                in_place_bugcheck=rejection, unchanged_on_rejection=True,
                nonpresent_ptes_during_gap=sum(not (p&1) for p in gap),
                remap_same_address=True, restored_initial_ptes=True, guards_intact=True,
                modeled_helpers=r.calls))
    result = dict(passed=True, scope=__doc__, physical_access=False, guest_launched=False,
        ordinary_qualified=False, kernel_sha256=sha(binary), inventory_sha256=sha(KIT/'inventory.json'),
        source_sha256=sha(Path(__file__)), io_cases=io_cases, reserved_cases=reserved_cases,
        previous_replay_correction={
            'source': 'outputs/video-cache-handoff/map-replay.json',
            'sha256': sha(WS/'outputs/video-cache-handoff/map-replay.json'),
            'reason': 'Historical labels for helper RVAs 0x69098 and 0x63d14 were reversed. Actual order is KeFlushCurrentTb then KeInvalidateAllCaches(1). Historical bytes, addresses and PTE results remain unchanged.'},
        limits='Allocation/cache/TLB helper side effects are modeled, not executed on hardware. Actual reserved-map/unmap instructions execute against synthetic MDLs/PTEs. A nonpresent PTE interval is demonstrated; no crash is injected in a running Windows guest. This does not prove all possible WC architectures impossible.')
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True, map_cases=len(io_cases), reserved_cases=len(reserved_cases),
        in_place_rejections=len(reserved_cases), remap_gaps=len(reserved_cases))))


if __name__ == '__main__':
    main()
