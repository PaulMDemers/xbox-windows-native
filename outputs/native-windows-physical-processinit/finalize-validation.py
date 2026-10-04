from pathlib import Path
import datetime,hashlib,json,shutil
kit=Path(__file__).resolve().parent;root=kit.parent.parent
cases=[('wide-001',True,1024),('normal-001',True,640),('trace-001',True,1024),('bad-hal-001',False,1024),('bad-kernel-001',False,1024)]
results=[]
for suffix,entered,width in cases:
 run='physical-processinit-'+suffix;src=root/'work/runs'/run;dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True)
 for name in ['entry-check.json','audited-framebuffer.png','input-hashes.json','entry-trace.json','launch.json']:
  if (src/name).exists():shutil.copy2(src/name,dst/name)
 r=json.loads((src/'entry-check.json').read_text())
 assert r['kernel_entered']==entered and r['framebuffer_mapping']['width']==width
 assert r['mapped_import_entries_verified']==1388 and r['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']
 assert r['status']==('kernel_process_initialization_verified' if entered else 'kernel_contract_rejected_before_entry' if 'bad-kernel' in suffix else 'unarmed_hal_rejected_before_kernel')
 if entered:
  e=r['entry_record']['words'];assert len(e)==320 and e[24]==220 and e[293]==1
  assert r['process_initialization']['working_set_dwords_verified']==1024 and r['process_initialization']['hash_page_zero_bytes_verified']==4096
  assert r['free_lists']['all_pfn_and_color_bytes_match'] and r['system_ptes']['all_system_ptes_verified']==22702
  assert sum(r['free_lists'][n] for n in ['available','new_inuse','preserved'])+626==0x3c00
  assert not r['storage_initialization_reached'] and not r['partition_handlers_entered']
 results.append({'run':run,'status':r['status'],'width':width,'imports_verified':1388})
trace=json.loads((root/'work/runs/physical-processinit-trace-001/entry-trace.json').read_text());assert trace['passed']
assert len(trace['events'])==1358
for name in ['PtGuardReturned','CommitGuardReturned','FreeGuardReturned','SysGuardReturned','ProcessGuardReturned']:
 event=next(e for e in trace['events'] if e['name']==name)
 assert event.get('registers_flags_and_frame_preserved',event.get('registers_and_flags_preserved'))
assert [e['name'] for e in trace['events'][-5:]]==['ProcessCheckpoint','ProcessGuardReturned','ProcessInitEntry','NativeInitReturn','InitCheckpoint']
end=next(e for e in trace['events'] if e['name']=='NativeInitReturn');assert end['native_status']==0 and end['full_process_delta_verified'] and end['thread_state_restored']
negatives=[]
for suffix,kind in [('init-input-001','init-input'),('process-object-001','process-object'),('hash-page-001','hash-page'),('corrupt-001','pfn')]:
 run='physical-processinit-'+suffix;src=root/'work/runs'/run/'entry-trace.json';r=json.loads(src.read_text())
 assert r['passed'] and r['corruption_rejected_without_repair']==kind and r['final_record'][3]==40
 dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst/src.name);negatives.append(kind)
assert json.loads((kit/'normal-hal-audit.json').read_text())['ordinary_hal_cannot_arm_probe']
assert 'PROCESSINIT probe requires PROCESSPAGES preflight' in (kit/'build-logs/forbidden-entry.log').read_text()
patch=json.loads((kit/'patch-check-0044.json').read_text());assert patch['working_tree_matches_chain']
for log in ['normal-loader.log','hal-normal.log']:
 p=kit/'build-logs'/log
 assert p.exists() and 'FAILED:' not in p.read_text() and 'Build files have been written' in p.read_text()
files=[{'path':p.relative_to(kit/'package').as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((kit/'package').rglob('*')) if p.is_file()]
assert len(files)==33
r={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready_for_physical_upload':True,'installed_on_physical_console':False,'physical_tested':False,'scope':'Initial process address space initialized; halt before further MM initialization and storage.','results':results,'trace_events':1358,'negative_tests':negatives,'package':files,'source_tree':patch['result_tree'],'expected_physical_success':'XWNW90: Process address space initialized.'}
(kit/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('Process initialization validated; ready for physical upload.')
