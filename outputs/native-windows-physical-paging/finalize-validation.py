from pathlib import Path
import datetime, hashlib, json, re, shutil

kit = Path(__file__).resolve().parent
root = kit.parent.parent
good_id = 'physical-paging-good-003'
bad_id = 'physical-paging-bad-nls-001'
dst = kit / 'evidence' / bad_id
dst.mkdir(parents=True, exist_ok=True)
for name in ['frame-075.png', 'frame-075.json', 'paging-check.json', 'launch.json', 'input-hashes.json']:
    shutil.copy2(root / 'work/runs' / bad_id / name, dst / name)
good = json.loads((kit / 'evidence' / good_id / 'paging-check.json').read_text())
bad = json.loads((dst / 'paging-check.json').read_text())
assert good['status'] == 'physical_paging_halt_verified'
assert good['kernel_entered'] is False
assert good['mapped_import_entries_verified'] == 1388
assert good['memory_descriptors_cover_64_mib_without_gaps_or_overlaps']
assert bad['status'] == 'no_completed_record'
bad_cr0 = int(re.search(r'CR0=([0-9a-fA-F]+)', bad['registers'])[1], 16)
assert not bad_cr0 & 0x80000000
audit = json.loads((kit / 'package-audit.json').read_text())
assert len(audit) == 33
for name, expected in audit.items():
    data = (kit / 'package' / name).read_bytes()
    assert len(data) == expected['bytes']
    assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
cache = Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build/handoff/CMakeCache.txt').read_text()
flags = dict(re.findall(r'^(XBOX_NATIVE_\w+):BOOL=(ON|OFF)$', cache, re.M))
for flag, expected in [('FATX_PAGING_PREFLIGHT','ON'), ('FATX_NT5_PREFLIGHT','ON'), ('NT5_ENTER','OFF'), ('NT5_AUTORUN','OFF')]:
    assert flags['XBOX_NATIVE_' + flag] == expected
patch = json.loads((kit / 'patch-check-0020.json').read_text())
assert patch['working_tree_matches_chain'] and patch['reverse_check'] and patch['whitespace_check']
result = {
    'validated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'ready_for_physical_upload': True,
    'physical_tested': False,
    'installed_on_physical_console': False,
    'kernel_entered': False,
    'scope': 'Emulator-verified paging diagnostic; unconditional halt before Windows kernel entry. Physical result pending.',
    'source_tree': patch['result_tree'],
    'build_flags': flags,
    'normal_loader_build_passed': True,
    'forbidden_entry_configuration_rejected': True,
    'missing_parent_configuration_rejected': True,
    'package_files_verified': len(audit),
    'success_run': good_id,
    'negative_run': {'id': bad_id, 'missing_file': 'c_1252.nls', 'status': bad['status'], 'cr0': hex(bad_cr0), 'paging_reached': False, 'visible_error': 'Error reading NLS file'},
    'emulator_checks': {k: good[k] for k in ['mapped_import_entries_verified', 'mapped_code_integrity', 'framebuffer_mapping', 'no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero', 'memory_descriptors_cover_64_mib_without_gaps_or_overlaps', 'lists_have_valid_backlinks', 'cr0', 'cr3', 'hive_bytes']},
    'modules': len(good['modules']),
    'boot_drivers': len(good['boot_drivers']),
    'memory_descriptors': len(good['memory_descriptors']),
    'development_runs': [
        {'id': 'physical-paging-good-001', 'result': 'Guard rejected incorrect expectation of 64 MiB managed RAM; corrected to 60 MiB plus reserved video RAM.'},
        {'id': 'physical-paging-good-002', 'result': 'Guard detected omitted framebuffer reservation at exclusive managed-memory boundary; comparison corrected.'}
    ]
}
assert (result['modules'], result['boot_drivers'], result['memory_descriptors']) == (20, 14, 24)
(kit / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
print('Validated 33 package files, paging success and missing-NLS failure; ready to upload.')
