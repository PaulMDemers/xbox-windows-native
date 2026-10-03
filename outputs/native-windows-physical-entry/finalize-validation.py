from pathlib import Path
import datetime,hashlib,json,shutil
kit=Path(__file__).resolve().parent;root=kit.parent.parent
cases=[('physical-entry-wide-003',True,1024),('physical-entry-normal-001',True,640),('physical-entry-bad-hal-001',False,1024),('physical-entry-trace-002',True,1024)]
results=[]
for run,entered,width in cases:
    src=root/'work/runs'/run;dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True)
    for name in ['entry-check.json','audited-framebuffer.png','input-hashes.json']:
        shutil.copy2(src/name,dst/name)
    for name in ['entry-trace.json','launch.json']:
        if (src/name).exists():shutil.copy2(src/name,dst/name)
    r=json.loads((dst/'entry-check.json').read_text())
    assert r['kernel_entered']==entered
    assert r['status']==('first_native_hal_checkpoint_verified' if entered else 'unarmed_hal_rejected_before_kernel')
    assert r['framebuffer_mapping']['width']==width
    assert r['mapped_import_entries_verified']==1388
    assert r['memory_descriptors_cover_64_mib_without_gaps_or_overlaps']
    assert r['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']
    if entered:
        assert not r['original_hal_processor_init_executed']
        assert r['expected_kernel_mutation']['entries']==256
        assert r['native_callsite']['instruction'].startswith('ff15')
    results.append({'run':run,'status':r['status'],'kernel_entered':entered,'framebuffer':r['framebuffer_mapping'],'imports_verified':r['mapped_import_entries_verified']})
trace=json.loads((kit/'evidence/physical-entry-trace-002/entry-trace.json').read_text())
assert trace['passed']
assert [e['name'] for e in trace['events']]==['KernelEntry','HalInitializeProcessor','LoaderCheckpoint']
audit={}
for p in sorted((kit/'package').rglob('*')):
    if p.is_file():
        b=p.read_bytes();audit[p.relative_to(kit/'package').as_posix()]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
assert len(audit)==33
assert audit['WINNT/system32/ntoskrnl.exe']['sha256']=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
old=kit.parent/'native-windows-physical-paging-v3/package'
changed=[n for n in audit if (kit/'package'/n).read_bytes()!=(old/n).read_bytes()]
assert set(changed)=={'README.txt','rosload.exe','loader/halxboxnt5.dll'}
(kit/'package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
patch=json.loads((kit/'patch-check-0023.json').read_text())
assert patch['working_tree_matches_chain'] and patch['reverse_check'] and patch['whitespace_check']
result={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'ready_for_physical_upload':True,'physical_tested':False,'physical_kernel_entry_confirmed':False,
        'installed_on_physical_console':False,'source_tree':patch['result_tree'],
        'scope':'Windows kernel executes through first HalInitializeProcessor call, then diagnostic halts before original HAL processor initialization. No desktop or driver startup claimed.',
        'normal_loader_build_passed':True,'normal_hal_build_passed':True,
        'missing_paging_parent_rejected':True,'diagnostic_hal_system_init_statically_verified_halt_only':True,
        'kernel_file_unchanged':True,'changed_files':changed,'package_files_verified':33,
        'emulator_tests':results,'native_trace_passed':True,
        'development_findings':['First attempt rejected the HAL because module names were compared without their explicit lengths; corrected before final binaries.','Initial post-entry audit rejected the expected IDT template field swaps; pinned-kernel startup instructions were inspected and the exact 256-entry transformation is now reproduced.','Initial debugger harness stop handshake timed out; repaired by stopping the owned VM and requesting its stop status.'],
        'expected_physical_success':'XWNK90: Windows kernel reached first HAL checkpoint.'}
(kit/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('All entry checks passed; three changed files ready for upload.')
