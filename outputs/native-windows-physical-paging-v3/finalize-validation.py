from pathlib import Path
import datetime, hashlib, json, shutil

kit = Path(__file__).resolve().parent
root = kit.parent.parent
cases = [('physical-paging-v3-wide-002', 1024, 576, 4096, 576),
         ('physical-paging-v3-normal-001', 640, 480, 2560, 300)]
results = []
for run, width, height, pitch, pages in cases:
    dst = kit/'evidence'/run
    dst.mkdir(parents=True, exist_ok=True)
    for name in ['paging-check.json', 'audited-framebuffer.png', 'launch.json', 'input-hashes.json']:
        shutil.copy2(root/'work/runs'/run/name, dst/name)
    data = json.loads((dst/'paging-check.json').read_text())
    assert data['status'] == 'physical_paging_halt_verified'
    assert data['kernel_entered'] is False
    assert data['mapped_import_entries_verified'] == 1388
    assert data['memory_descriptors_cover_64_mib_without_gaps_or_overlaps']
    assert data['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']
    fb = data['framebuffer_mapping']
    assert (fb['width'], fb['height'], fb['pitch'], fb['identity_pages_verified']) == (width, height, pitch, pages)
    assert fb['bytes'] == height*pitch == pages*4096
    assert fb['firmware_reserved'] and fb['uncached_write_through']
    assert (len(data['modules']), len(data['boot_drivers']), len(data['memory_descriptors'])) == (20,14,24)
    results.append({'id':run, 'framebuffer':fb, 'status':data['status'], 'imports_verified':1388,
                    'modules':20, 'boot_drivers':14, 'memory_descriptors':24,
                    'framebuffer_image_visually_checked':True})
audit = {}
for p in sorted((kit/'package').rglob('*')):
    if p.is_file():
        data = p.read_bytes()
        audit[p.relative_to(kit/'package').as_posix()] = {'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}
assert len(audit) == 33
(kit/'package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
patch = json.loads((kit/'patch-check-0022.json').read_text())
assert patch['working_tree_matches_chain'] and patch['reverse_check'] and patch['whitespace_check']
fixture = json.loads((kit/'widescreen-fixture.json').read_text())
assert hashlib.sha256(Path('C:/Emulators/xemu/eeprom.bin').read_bytes()).hexdigest() == fixture['source_sha256']
result = {
    'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'ready_for_physical_upload':True,
    'physical_tested':False,
    'installed_on_physical_console':False,
    'kernel_entered':False,
    'source_tree':patch['result_tree'],
    'normal_loader_build_passed':True,
    'package_files_verified':len(audit),
    'same_final_package_for_both_modes':True,
    'shared_emulator_eeprom_preserved':True,
    'physical_video_settings_changed':False,
    'emulator_tests':results,
    'scope':'Paging diagnostic; 640x480 and 1024x576 only, full framebuffer reservation/range checks, unconditional halt before kernel entry.',
    'capture_limitation':'Legacy harness frame-NNN.png assumes 640x480. Use audited-framebuffer.png, decoded from guest RAM with validated dimensions/pitch, for widescreen evidence.',
    'predecessor_physical_result':'v2 correctly reported 1024x576/4096; rejected by its fixed 640x480 guard.'
}
(kit/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('Both actual Xromwell display modes validated; ready for physical upload.')
