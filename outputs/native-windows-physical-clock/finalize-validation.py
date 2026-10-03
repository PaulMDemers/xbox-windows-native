from pathlib import Path
import datetime,hashlib,json,shutil
kit=Path(__file__).resolve().parent;root=kit.parent.parent
cases=[('physical-clock-wide-002',True,1024),('physical-clock-normal-001',True,640),('physical-clock-bad-hal-001',False,1024),('physical-clock-trace-001',True,1024)]
results=[]
for run,entered,width in cases:
 src=root/'work/runs'/run;dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True)
 for name in ['entry-check.json','audited-framebuffer.png','input-hashes.json']:
  shutil.copy2(src/name,dst/name)
 for name in ['entry-trace.json','launch.json']:
  if (src/name).exists():shutil.copy2(src/name,dst/name)
 r=json.loads((dst/'entry-check.json').read_text())
 assert r['kernel_entered']==entered
 assert r['status']==('clock_setup_boundary_verified' if entered else 'unarmed_hal_rejected_before_kernel')
 assert r['framebuffer_mapping']['width']==width
 assert r['mapped_import_entries_verified']==1388
 assert r['memory_descriptors_cover_64_mib_without_gaps_or_overlaps']
 assert r['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']
 if entered:
  assert r['original_hal_processor_init_executed'] and r['original_hal_phase0_body_executed'] and not r['hal_phase0_completed']
  assert r['expected_kernel_mutation']['entries']==256
  assert r['timer_calibration_returned'] and r['clock_initialization_reached'] and not r['storage_initialization_reached']
 results.append({'run':run,'status':r['status'],'kernel_entered':entered,'framebuffer':r['framebuffer_mapping'],'imports_verified':r['mapped_import_entries_verified']})
trace=json.loads((kit/'evidence/physical-clock-trace-001/entry-trace.json').read_text())
assert trace['passed']
assert next(e for e in trace['events'] if e['name']=='FirstRtcInterrupt')['rtc_interrupt_count_before_increment']==0
assert next(e for e in trace['events'] if e['name']=='SecondRtcInterrupt')['rtc_interrupt_count']==2
assert [e['name'] for e in trace['events']]==['KernelEntry','HalInitializeProcessor','ProcessorReturned','HalInitSystem','BaseHalReady','CalibrationEntry','FirstRtcInterrupt','SecondRtcInterrupt','CalibrationReturned','TimerReady','ClockInitialize','KernelSetTimeIncrement','PitModeWrite','PitLowWrite','PitHighWrite','ClockReturned','ProfileStop','ProfileReturned','ClockReady','LoaderCheckpoint']
assert len(trace['forbidden_breakpoints'])==19 # 17 loaded .sys modules and 2 storage boundaries
boundary=json.loads((kit/'hal-boundary-audit.json').read_text())
assert boundary['hal_storage_unreachable_after_clock_stop'] and boundary['processor_has_before_after_calls_and_return']
assert json.loads((kit/'normal-hal-audit.json').read_text())['ordinary_hal_cannot_arm_probe']
audit={}
for p in sorted((kit/'package').rglob('*')):
 if p.is_file():
  b=p.read_bytes();audit[p.relative_to(kit/'package').as_posix()]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
assert len(audit)==33
assert audit['WINNT/system32/ntoskrnl.exe']['sha256']=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
assert audit['loader/halxboxnt5.dll']['sha256']==boundary['sha256']
old=kit.parent/'native-windows-physical-timer/package'
changed=[n for n in audit if (kit/'package'/n).read_bytes()!=(old/n).read_bytes()]
assert set(changed)=={'README.txt','rosload.exe','loader/halxboxnt5.dll'}
(kit/'package-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
patch=json.loads((kit/'patch-check-0027.json').read_text())
assert patch['working_tree_matches_chain'] and patch['reverse_check'] and patch['whitespace_check']
assert 'Clock probe requires timer preflight' in (kit/'build-logs/forbidden-entry.log').read_text()
for log in ['normal-loader.log','hal-normal.log']:
 text=(kit/'build-logs'/log).read_text();assert 'FAILED:' not in text and 'error:' not in text
result={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'ready_for_physical_upload':True,'physical_tested':False,'installed_on_physical_console':False,
 'source_tree':patch['result_tree'],
 'scope':'RTC calibration and clock setup returned; native time-increment values, PIT programming and RTC profiling stop checked. Halt before Xbox storage and drivers.',
 'normal_loader_build_passed':True,'normal_hal_build_passed':True,
 'missing_timer_parent_rejected':True,'post_clock_halt_statically_verified':True,
 'kernel_file_unchanged':True,'changed_files':changed,'package_files_verified':33,
 'emulator_tests':results,'native_trace_passed':True,
 'development_findings':['The first diagnostic used generic PC clock-table constants. Its guard rejected the actual Xbox-specific values and halted before storage. The check was corrected to the linked hal/halx86/xbox/clock.c values: 16875 reload, 150000 maximum and 10000 minimum increment.'],
 'expected_physical_success':'XWNC90: Clock configured; stopped before storage.',
 'fixture_package_includes_final_readme':True}
(kit/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('Clock validation complete; three changed files ready for upload.')
