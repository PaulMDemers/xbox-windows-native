from pathlib import Path
import datetime, hashlib, json, re, shutil

kit = Path(__file__).resolve().parent
root = kit.parent.parent
good_id, guard_id = 'physical-paging-v2-good-001', 'physical-paging-v2-guard-001'
for run in [good_id, guard_id]:
    dst = kit / 'evidence' / run
    dst.mkdir(parents=True, exist_ok=True)
    for name in ['paging-check.json', 'frame-045.png', 'frame-045.json', 'launch.json', 'input-hashes.json']:
        shutil.copy2(root / 'work/runs' / run / name, dst / name)
good = json.loads((kit / 'evidence' / good_id / 'paging-check.json').read_text())
guard = json.loads((kit / 'evidence' / guard_id / 'paging-check.json').read_text())
assert good['status'] == 'physical_paging_halt_verified'
assert good['kernel_entered'] is False
assert good['mapped_import_entries_verified'] == 1388
assert good['memory_descriptors_cover_64_mib_without_gaps_or_overlaps']
assert guard['status'] == 'no_completed_record'
assert 'HLT=1' in guard['registers']
assert not int(re.search(r'CR0=([0-9a-fA-F]+)', guard['registers'])[1], 16) & 0x80000000
audit = {}
for p in sorted((kit / 'package').rglob('*')):
    if p.is_file():
        data = p.read_bytes()
        audit[p.relative_to(kit/'package').as_posix()] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
assert len(audit) == 33
assert (kit/'package/rosload.exe').read_bytes() != (root/'work/paging-v2-forced-guard.exe').read_bytes()
(kit/'package-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
patch = json.loads((kit/'patch-check-0021.json').read_text())
assert patch['working_tree_matches_chain'] and patch['reverse_check'] and patch['whitespace_check']
result = {
    'validated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'ready_for_physical_upload': True,
    'physical_tested': False,
    'installed_on_physical_console': False,
    'kernel_entered': False,
    'source_tree': patch['result_tree'],
    'scope': 'Guard reporting only; all physical paging acceptance checks remain unchanged.',
    'normal_loader_build_passed': True,
    'success_run': good_id,
    'forced_guard_run': guard_id,
    'forced_guard_method': 'Separate emulator-only rosload expects width 641. Final source/package expects 640. Forced binary excluded from physical package.',
    'forced_guard_screen_visually_checked': True,
    'forced_guard_cpu_halted_before_paging': True,
    'package_files_verified': len(audit),
    'mapped_import_entries_verified': good['mapped_import_entries_verified'],
    'framebuffer_mapping': good['framebuffer_mapping'],
    'memory_descriptors_cover_64_mib_without_gaps_or_overlaps': True,
    'modules': len(good['modules']),
    'boot_drivers': len(good['boot_drivers']),
    'memory_descriptors': len(good['memory_descriptors']),
    'predecessor_physical_result': 'v1 guard rejected framebuffer/RAM layout; individual value unknown until v2 is run.'
}
assert (result['modules'], result['boot_drivers'], result['memory_descriptors']) == (20, 14, 24)
(kit/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
print('V2 validated; physical upload may proceed.')
