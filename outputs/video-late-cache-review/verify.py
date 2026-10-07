"""Audit the completed read-only review without rerunning or changing its evidence."""
import ast
import hashlib
import json
from pathlib import Path

KIT = Path(__file__).resolve().parent
WS = KIT.parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inv, replay, shadow = (read(KIT/n) for n in ['inventory.json','replay.json','shadow-contract.json'])
    assert inv['passed'] and replay['passed'] and shadow['passed']
    assert not inv['guest_launched'] and not replay['guest_launched']
    assert not inv['physical_access'] and not replay['physical_access']
    assert not replay['ordinary_qualified']
    for name, field, record in [('inventory.py','script_sha256',inv),('replay.py','source_sha256',replay),('shadow-contract.py','source_sha256',shadow)]:
        assert sha(KIT/name) == record[field]
    assert sha(Path(inv['kernel_path'])) == inv['kernel_sha256'] == replay['kernel_sha256']
    assert sha(Path(inv['trace_path'])) == inv['trace_sha256']
    assert sha(Path(inv['memory_path'])) == inv['memory_sha256']
    assert sha(WS/'outputs/native-windows-nt5-kernel/kernel-publics.json') == inv['symbols_sha256']
    assert sha(WS/'outputs/video-cache-handoff/map-sites.json') == inv['metadata_sha256']
    assert sha(KIT/'inventory.json') == replay['inventory_sha256']
    functions = inv['functions']
    assert len(functions) == 18
    assert sum(f['resident_sha256'] is not None for f in functions.values()) == 17
    assert sum(f['resident_matches_disk'] is True for f in functions.values()) == 16
    assert functions['_KeFlushCurrentTb@0']['resident_variant']['active_bytes'] == 20
    assert functions['_MmSetPageProtection@12']['resident_sha256'] is None
    syms = read(WS/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols']
    helpers = {'MiReserveSystemPtes':20,'MiReleaseSystemPtes':12,'KeFlushCurrentTb':0,'KeInvalidateAllCaches':4}
    assert len(replay['io_cases']) == 7 and len(replay['reserved_cases']) == 8
    for case in replay['io_cases'] + replay['reserved_cases']:
        for helper in case['modeled_helpers']:
            name = helper['name']
            assert helper['rva'] == syms[f'_{name}@{helpers[name]}']['rva']
            assert len(helper['arguments'])*4 == helpers[name]
            assert helper['modeled']
    for case in replay['reserved_cases']:
        assert case['in_place_bugcheck'][:2] == [0xda,0x107]
        assert case['nonpresent_ptes_during_gap'] == case['pages']
        assert case['guards_intact'] and case['restored_initial_ptes'] and case['unchanged_on_rejection']
    correction = replay['previous_replay_correction']
    assert sha(WS/correction['source']) == correction['sha256']
    failure = read(KIT/'initial-inspection-failure.json')
    assert sha(KIT/'inspect-initial.py') == failure['source_sha256']
    assert sha(Path(shadow['binary_path'])) == shadow['binary_sha256']
    assert len(shadow['needed_engine_exports']) == 32
    assert all(v is not None for v in shadow['source_engine_references'].values())
    for name, digest in shadow['source_files'].items():
        assert sha(Path(shadow['source_root'])/name) == digest
    scripts = sorted(KIT.glob('*.py'))
    for path in scripts:
        ast.parse(path.read_text())
    print(json.dumps(dict(passed=True, resident_windows=17, exact_PE_matches=16,
        explicit_CR4_variant=1, map_cases=7, reserved_cases=8,
        needed_engine_exports=32, parsed_scripts=len(scripts), physical_access=False, guest_launched=False)))


if __name__ == '__main__':
    main()
