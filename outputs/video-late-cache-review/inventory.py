"""Read-only inventory of pinned NT5 mapping code and an existing RAM capture."""
import hashlib
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
WS = KIT.parents[1]
sys.path.insert(0, str(WS / 'work/python-packages'))
sys.path.insert(0, str(WS / 'outputs/video-cache-handoff'))
import capstone
import pefile
from walk import read_virtual


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    dest = KIT / 'inventory.json'
    assert not dest.exists(), 'Do not overwrite evidence'
    meta_path = WS / 'outputs/video-cache-handoff/map-sites.json'
    symbols_path = WS / 'outputs/native-windows-nt5-kernel/kernel-publics.json'
    trace_path = WS / 'outputs/video-shared-trace2/trace002/trace.json'
    meta = read(meta_path)['modules']['ntoskrnl.exe']
    binary = Path(meta['path'])
    assert sha(binary) == meta['sha256'] == '84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
    syms = read(symbols_path)['symbols']
    trace = read(trace_path)
    memory = Path(trace['private_memory'])
    assert sha(memory) == trace['private_memory_sha256']
    ram = memory.read_bytes()
    pe = pefile.PE(str(binary))
    exports = {s.name.decode(): s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    sorted_syms = sorted((v['rva'], n) for n, v in syms.items())
    reverse = {}
    for rva, name in sorted_syms:
        reverse.setdefault(rva, []).append(name)
    base = trace['kernel_base']
    pe.relocate_image(base)
    image = pe.get_memory_mapped_image()
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    names = [
        '_MmMapIoSpace@16', '_MmUnmapIoSpace@8',
        '_MmMapLockedPagesSpecifyCache@24', '_MmAllocateMappingAddress@8',
        '_MmMapLockedPagesWithReservedMapping@16', '_MmUnmapReservedMapping@12',
        '_MmSetPageProtection@12', '_KeFlushCurrentTb@0', '_KeInvalidateAllCaches@4',
        '_InbvAcquireDisplayOwnership@0', '_InbvCheckDisplayOwnership@0',
        '_InbvNotifyDisplayOwnershipLost@4', '_InbvAcquireLock@0',
        '_InbvReleaseLock@0', '_InbvResetDisplay@0', '_InbvDisplayString@4',
        '_InbvSolidColorFill@20', '_MiReleaseSystemPtes@12',
    ]
    functions = {}
    for name in names:
        rva = syms[name]['rva']
        end = next(a for a, n in sorted_syms if a > rva)
        # This INIT symbol is followed by data before the next public symbol.
        if name == '_MmSetPageProtection@12':
            end = 0x1548a7
        data = image[rva:end]
        section = pe.get_section_by_rva(rva)
        discarded_section = bool(section.Characteristics & 0x02000000)
        instructions = []
        for ins in decoder.disasm(data, base + rva):
            row = dict(rva=ins.address - base, mnemonic=ins.mnemonic, operands=ins.op_str)
            if ins.mnemonic in ('call', 'jmp') and ins.op_str.startswith('0x'):
                target = int(ins.op_str, 16) - base
                row.update(target_rva=target, public_names=reverse.get(target, []))
            instructions.append(row)
        resident = None
        resident_matches_disk = None
        resident_variant = None
        if not discarded_section:
            actual = read_virtual(ram, trace['control_registers']['CR3'], base + rva, len(data))
            resident_matches_disk = actual == data
            if not resident_matches_disk:
                # The active CR4.PGE flush sequence occupies the entry that has
                # the CR3 reload sequence on disk. Do not claim full PE equality.
                assert name == '_KeFlushCurrentTb@0', name
                assert actual[:20] == data[7:27]
                resident_variant = dict(active_bytes=20, active_sha256=hashlib.sha256(actual[:20]).hexdigest(),
                    disk_matching_offset=7,
                    instructions=[dict(rva=i.address-base, mnemonic=i.mnemonic, operands=i.op_str)
                        for i in decoder.disasm(actual[:20], base+rva)])
            resident = hashlib.sha256(actual).hexdigest()
        functions[name] = dict(rva=rva, end_rva=end, bytes=len(data),
            section=section.Name.rstrip(b'\0').decode(), section_flags=section.Characteristics,
            discardable_section=discarded_section,
            exports=[n for n, a in exports.items() if a == rva],
            relocated_sha256=hashlib.sha256(data).hexdigest(),
            resident_sha256=resident, resident_matches_disk=resident_matches_disk,
            resident_variant=resident_variant, instructions=instructions)
    checks = {
        'MmProtectMdlSystemAddress_absent': 'MmProtectMdlSystemAddress' not in exports,
        'MmSetPageProtection_not_exported': 'MmSetPageProtection' not in exports,
        'MmSetPageProtection_INIT_discardable': functions['_MmSetPageProtection@12']['discardable_section'],
        'reserved_mapping_present': exports['MmMapLockedPagesWithReservedMapping'] == 0x37884,
        'helper_69098_is_KeFlushCurrentTb': syms['_KeFlushCurrentTb@0']['rva'] == 0x69098,
        'helper_63d14_is_KeInvalidateAllCaches': syms['_KeInvalidateAllCaches@4']['rva'] == 0x63d14,
    }
    assert all(checks.values())
    result = dict(passed=True, scope=__doc__, physical_access=False, guest_launched=False,
        kernel_path=str(binary), kernel_sha256=sha(binary), kernel_base=base,
        trace_path=str(trace_path), trace_sha256=sha(trace_path),
        memory_path=str(memory), memory_sha256=sha(memory),
        symbols_sha256=sha(symbols_path), metadata_sha256=sha(meta_path),
        script_sha256=sha(Path(__file__)), checks=checks, functions=functions,
        relevant_exports={n: r for n, r in exports.items() if any(t in n for t in ('Map', 'Cache', 'Protect', 'Flush', 'Inbv'))},
        limits='Read-only analysis of one owned kernel and a previous closed desktop capture. INIT inspected only on disk; not invoked. Public-symbol windows can include padding. No new runtime transition, TLB observation or physical test.')
    dest.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, functions=len(functions), resident_pins=sum(f['resident_sha256'] is not None for f in functions.values()), checks=checks)))


if __name__ == '__main__':
    main()
