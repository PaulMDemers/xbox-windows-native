from pathlib import Path
import datetime,hashlib,json,shutil
kit=Path(__file__).resolve().parent;root=kit.parent.parent
cases=[('physical-pfncommit-wide-001',True,1024),('physical-pfncommit-normal-001',True,640),('physical-pfncommit-bad-hal-001',False,1024),('physical-pfncommit-trace-001',True,1024),('physical-pfncommit-bad-kernel-001',False,1024)]
results=[]
map_audit=json.loads((kit/'map-boundary-audit.json').read_text())
assert map_audit['cr3_flush_instruction_present'] and map_audit['checkpoint_has_halt_and_no_return']
review=json.loads((kit/'descriptor-accounting-review.json').read_text())
assert review['stop_before_free_list_construction'] and review['preallocation_guard_required']
for run,entered,width in cases:
 src=root/'work/runs'/run;dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True)
 for name in ['entry-check.json','audited-framebuffer.png','input-hashes.json']:
  shutil.copy2(src/name,dst/name)
 for name in ['entry-trace.json','launch.json']:
  if (src/name).exists():shutil.copy2(src/name,dst/name)
 r=json.loads((dst/'entry-check.json').read_text())
 assert r['kernel_entered']==entered
 assert r['status']==('kernel_descriptor_accounting_verified' if entered else ('kernel_contract_rejected_before_entry' if 'bad-kernel' in run else 'unarmed_hal_rejected_before_kernel'))
 assert r['framebuffer_mapping']['width']==width
 assert r['mapped_import_entries_verified']==1388
 assert r['descriptors_and_native_allocations_cover_64_mib']
 assert r['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']
 if entered:
  assert r['descriptor_reconciliation']['full_accounting_verified'] and r['descriptor_reconciliation']['restored_pages']==622
  assert r['mapped_pfns']['all_pfn_bytes_match_model'] and r['mapped_pfns']['all_paging_entries_match_model']
  assert r['mapped_pfns']['color_heads']==64 and not r['pfn_backing']['color_page_descriptor_commit_pending']
  assert r['pool_initialized']['pool_initialized'] and r['pool_initialized']['page_owner_links_verified']==500
  assert r['pool_backing']['pages_mapped']==504 and r['pool_backing']['all_ptes_verified']
  assert r['original_hal_processor_init_executed'] and r['original_hal_phase0_body_executed'] and r['hal_phase0_completed']
  assert r['expected_kernel_mutation']['entries']==256
  assert r['low_mapping_transition']['absent_low_pdes']==512 and r['low_mapping_transition']['record_in_hal']
  assert r['ram_scan']['native_results_match_descriptor_model'] and r['ram_scan']['first_allocation_completed']
  assert r['memory_sizing']['native_results_match_model'] and r['memory_sizing']['pool_backing_mappings_verified']
  e=r['entry_record']['words'];symbols=map_audit['symbols_rva']
  assert e[88]==e[8]+int(symbols['_HalpXwnMapEntry'],16)
  assert e[94]==e[8]+int(symbols['_HalpXwnMapCheckpoint@4'],16)
  assert e[95]==e[8]+int(symbols['_XwnMapRecord'],16)
  assert r['partition_hooks_registered'] and not r['partition_handlers_entered'] and r['bios_initialization_reached'] and r['hal_phase0_body_completed'] and r['hal_phase0_returned']
  assert r['timer_calibration_returned'] and r['clock_initialization_reached'] and not r['storage_initialization_reached']
 results.append({'run':run,'status':r['status'],'kernel_entered':entered,'framebuffer':r['framebuffer_mapping'],'imports_verified':r['mapped_import_entries_verified']})
trace=json.loads((kit/'evidence/physical-pfncommit-trace-001/entry-trace.json').read_text())
assert trace['passed']
assert next(e for e in trace['events'] if e['name']=='MappedPfnsReady')['mapped_pfns']['all_pfn_bytes_match_model']
assert [e for e in trace['events'] if e['name']=='LowerReturned'][-1]['descriptor_list_unchanged_by_mapped_initialization']
assert next(e for e in trace['events'] if e['name']=='PfnBackingReady')['exact_descriptor_commit_verified']
assert len([e for e in trace['events'] if e['name']=='PfnWrite'])==90
assert len([e for e in trace['events'] if e['name']=='ColorWrite'])==1
assert all(e['pic_after'].count('imr=ff')==2 for e in trace['events'] if e['name'] in ['RaiseReturned','LowerReturned'])
assert next(e for e in trace['events'] if e['name']=='RegistryControlsReturned')['registry_control_data_verified']
assert next(e for e in trace['events'] if e['name']=='MemoryLimitsReturned')['descriptor_filter_total_verified']
assert next(e for e in trace['events'] if e['name']=='MachineDependentEntry')['memory_descriptors_unchanged_by_mm_prefix']
assert next(e for e in trace['events'] if e['name']=='LowMappingsCleared')['absent_low_pdes_after']==512
assert next(e for e in trace['events'] if e['name']=='MapCheckpoint')['native_mi_frame_verified']
assert next(e for e in trace['events'] if e['name']=='RamScanCompleted')['descriptor_list_unchanged']
assert next(e for e in trace['events'] if e['name']=='SizingCompleted')['descriptor_list_unchanged']
assert next(e for e in trace['events'] if e['name']=='FirstTablesCreated')['descriptor_list_unchanged']
assert next(e for e in trace['events'] if e['name']=='PoolInitialized')['write_delta']['only_expected_507_dword_writes']
assert next(e for e in trace['events'] if e['name']=='PoolMapped')['pool']['pool_backing_mappings_verified']
assert next(e for e in trace['events'] if e['name']=='PtGuardReturned')['registers_and_flags_preserved']
assert next(e for e in trace['events'] if e['name']=='BiosReturned')['exact_descriptor_transition_verified']
assert next(e for e in trace['events'] if e['name']=='HooksReady')['saved_originals_equal_pre_registration']
assert next(e for e in trace['events'] if e['name']=='FirstRtcInterrupt')['rtc_interrupt_count_before_increment']==0
assert next(e for e in trace['events'] if e['name']=='SecondRtcInterrupt')['rtc_interrupt_count']==2
assert [e['name'] for e in trace['events']]==['KernelEntry','HalInitializeProcessor','ProcessorReturned','HalInitSystem','BaseHalReady','CalibrationEntry','FirstRtcInterrupt','SecondRtcInterrupt','CalibrationReturned','TimerReady','ClockInitialize','KernelSetTimeIncrement','PitModeWrite','PitLowWrite','PitHighWrite','ClockReturned','ProfileStop','ProfileReturned','ClockReady','XboxPhase0','PartitionRegistration','HooksReady','BiosInitialize','BiosAllocateFirst','BiosAllocatedFirst','BiosAllocateSecond','BiosAllocatedSecond','BiosReturned','BiosReady','LoaderCheckpoint','HalPhase0Return','RegistryControls','RegistryControlsReturned','ExecutiveInit','ExecutiveReturned','MemoryManagerEntry','MemoryLimits','MemoryLimitsReturned','TriageSystem','TriageReturned','MachineDependentEntry','LowClearBegin','LowMappingsCleared','RamScanCompleted','SizingCompleted','PtGuard','PtGuardReturned']+['PdeWrite','TableZeroed']*28+['FirstTablesCreated','PoolMappingBegin']+['PoolPteWrite','PoolPteWritten']*504+['PoolMapped','PoolInitializerEntry','SystemPtesInit','FillPtes','PoolInitializerTail','PoolInitialized','ReserveFirst','RaiseIrql','RaiseReturned','LowerIrql','LowerReturned','ReservedFirst','ReserveSecond','RaiseIrql','RaiseReturned','LowerIrql','LowerReturned','ReservedSecond']+['PfnWrite','PfnZeroed']*90+['PfnDescriptorsDone','PfnDescriptorsCommitted','ColorWrite','ColorZeroed','PfnBackingReady','ColorsReady','MappedPfnsReady','RaiseIrql','RaiseReturned','LowerIrql','LowerReturned','DescriptorRecommit','MapCheckpoint']
assert len(trace['forbidden_breakpoints'])==35 # Driver/partition entries, alternate allocation paths, initializer and bugcheck
negative_source=root/'work/runs/physical-pfncommit-mapped-candidate-001/entry-trace.json'
negative=json.loads(negative_source.read_text())
assert negative['passed'] and negative['allocation_blocked'] and negative['candidate_bytes_unchanged']
assert negative['descriptor_list_unchanged'] and negative['injected_alias_restored']
assert negative['final_record'][3]==40 and negative['final_record'][139]==0
negative_dir=kit/'evidence/physical-pfncommit-mapped-candidate-001';negative_dir.mkdir(parents=True,exist_ok=True)
shutil.copy2(negative_source,negative_dir/'entry-trace.json')
profile_source=root/'work/runs/physical-pfncommit-profile-001/entry-trace.json'
profile=json.loads(profile_source.read_text());assert profile['passed'] and profile['bad_pool_profile_rejected'] and profile['allocation_blocked'] and profile['candidate_bytes_unchanged']
assert profile['final_record'][152]==0
profile_dir=kit/'evidence/physical-pfncommit-profile-001';profile_dir.mkdir(parents=True,exist_ok=True);shutil.copy2(profile_source,profile_dir/'entry-trace.json')
boundary=json.loads((kit/'hal-boundary-audit.json').read_text())
corrupt_source=root/'work/runs/physical-pfncommit-corrupt-001/entry-trace.json'
corrupt=json.loads(corrupt_source.read_text())
assert corrupt['passed'] and corrupt['corrupt_pfn_rejected_before_free_lists']
assert corrupt['final_record'][3]==40 and corrupt['final_record'][178]==0
corrupt_dir=kit/'evidence/physical-pfncommit-corrupt-001';corrupt_dir.mkdir(parents=True,exist_ok=True)
shutil.copy2(corrupt_source,corrupt_dir/'entry-trace.json')
bad_descriptor_source=root/'work/runs/physical-pfncommit-corrupt-descriptor-001/entry-trace.json'
bad_descriptor=json.loads(bad_descriptor_source.read_text())
assert bad_descriptor['passed'] and bad_descriptor['corrupt_descriptor_rejected_without_repair']
assert bad_descriptor['final_record'][195]==0 and bad_descriptor['final_record'][192]==0
bad_descriptor_dir=kit/'evidence/physical-pfncommit-corrupt-descriptor-001';bad_descriptor_dir.mkdir(parents=True,exist_ok=True)
shutil.copy2(bad_descriptor_source,bad_descriptor_dir/'entry-trace.json')
assert boundary['hal_phase0_returns_only_for_mm_probe'] and boundary['processor_has_before_after_calls_and_return']
assert json.loads((kit/'normal-hal-audit.json').read_text())['ordinary_hal_cannot_arm_probe']
audit={}
for p in sorted((kit/'package').rglob('*')):
 if p.is_file():
  b=p.read_bytes();audit[p.relative_to(kit/'package').as_posix()]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
assert len(audit)==33
assert audit['WINNT/system32/ntoskrnl.exe']['sha256']=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
assert audit['loader/halxboxnt5.dll']['sha256']==boundary['sha256']
assert audit['loader/halxboxnt5.dll']['sha256']==map_audit['hal_sha256']
old=kit.parent/'native-windows-physical-pfnmap/package'
changed=[n for n in audit if (kit/'package'/n).read_bytes()!=(old/n).read_bytes()]
assert set(changed)=={'README.txt','rosload.exe','loader/halxboxnt5.dll'}
(kit/'package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
patch=json.loads((kit/'patch-check-0040.json').read_text())
assert patch['working_tree_matches_chain'] and patch['reverse_check'] and patch['whitespace_check']
assert 'PFNCOMMIT probe requires PFNMAP preflight' in (kit/'build-logs/forbidden-entry.log').read_text()
for log in ['normal-loader.log','hal-normal.log']:
 text=(kit/'build-logs'/log).read_text();assert 'FAILED:' not in text and 'error:' not in text
result={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'ready_for_physical_upload':True,'physical_tested':False,'installed_on_physical_console':False,
 'source_tree':patch['result_tree'],
 'scope':'Native descriptor double subtraction reconciled; high HAL stops before free-page lists.',
 'normal_loader_build_passed':True,'normal_hal_build_passed':True,
 'missing_pfnmap_parent_rejected':True,'descriptor_accounting_halt_verified':True,
 'kernel_file_unchanged':True,'temporary_kernel_patch_restored':True,'unexpected_kernel_rejected':True,'changed_files':changed,'package_files_verified':33,
 'emulator_tests':results,'native_trace_passed':True,'pfn_backing_zero_before_population_verified':True,'full_pfn_population_model_verified':True,'existing_mapping_permission_changes_verified':True,'reservation_pic_masks_verified':True,'pool_write_delta_verified':True,'unexpected_pool_profile_rejected':True,'mapped_candidate_rejected_before_allocation':True,
 'corrupt_unused_pfn_word_rejected':True,'unexpected_descriptor_count_rejected_without_repair':True,'descriptor_pages_restored':622,
 'expected_physical_success':'XWNJ90: Descriptor accounting reconciled; lists blocked.',
 'fixture_package_includes_final_readme':True}
(kit/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('Descriptor reconciliation validated; three changed files ready for upload.')
