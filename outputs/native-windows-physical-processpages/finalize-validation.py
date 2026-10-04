from pathlib import Path
import datetime,hashlib,json,shutil
kit=Path(__file__).resolve().parent;root=kit.parent.parent
cases=[('wide-001',True,1024),('normal-001',True,640),('trace-002',True,1024),('bad-hal-001',False,1024),('bad-kernel-001',False,1024)]
results=[]
for suffix,entered,width in cases:
 run='physical-processpages-'+suffix;src=root/'work/runs'/run;dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True)
 for name in ['entry-check.json','audited-framebuffer.png','input-hashes.json','entry-trace.json','launch.json']:
  if (src/name).exists():shutil.copy2(src/name,dst/name)
 r=json.loads((src/'entry-check.json').read_text())
 assert r['kernel_entered']==entered and r['framebuffer_mapping']['width']==width
 assert r['mapped_import_entries_verified']==1388 and r['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']
 assert r['status']==('kernel_first_process_pages_verified' if entered else 'kernel_contract_rejected_before_entry' if 'bad-kernel' in suffix else 'unarmed_hal_rejected_before_kernel')
 if entered:
  e=r['entry_record']['words'];assert len(e)==288 and e[24]==210 and e[261]==1
  assert r['first_process_pages']['working_set_bytes_zero_verified']==4096 and r['first_process_pages']['pool_descriptor_list_heads_verified']==256
  assert r['free_lists']['all_pfn_and_color_bytes_match'] and r['system_ptes']['all_system_ptes_verified']==22702
  assert sum(r['free_lists'][n] for n in ['available','new_inuse','preserved'])+625==0x3c00
  assert not r['storage_initialization_reached'] and not r['partition_handlers_entered']
 results.append({'run':run,'status':r['status'],'width':width,'imports_verified':1388})
trace=json.loads((root/'work/runs/physical-processpages-trace-002/entry-trace.json').read_text());assert trace['passed']
assert len(trace['events'])==1353
for name in ['PtGuardReturned','CommitGuardReturned','FreeGuardReturned','SysGuardReturned']:
 event=next(e for e in trace['events'] if e['name']==name)
 assert event.get('registers_flags_and_frame_preserved',event.get('registers_and_flags_preserved'))
assert [e['name'] for e in trace['events'][-10:]]==['TailCheckpoint','SysGuardReturned','ExecutivePool','PoolReturned','RemovePage','FirstAllocated','FirstTableZeroed','RemovePage','SecondAllocated','ProcessCheckpoint']
assert trace['events'][-1]['process_object_unchanged']
negatives=[]
for suffix,kind in [('corrupt-working-set-001','working-set'),('corrupt-pte-001','system-pte'),('corrupt-link-001','free-link'),('corrupt-001','pfn'),('corrupt-descriptor-001','descriptor')]:
 run='physical-processpages-'+suffix;src=root/'work/runs'/run/'entry-trace.json';r=json.loads(src.read_text())
 assert r['passed'] and r['corruption_rejected_without_repair']==kind and r['final_record'][3]==40
 dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst/src.name);negatives.append(kind)
for suffix,flag in [('mapped-candidate-001','allocation_blocked'),('profile-001','bad_pool_profile_rejected')]:
 run='physical-processpages-'+suffix;src=root/'work/runs'/run/'entry-trace.json';r=json.loads(src.read_text());assert r['passed'] and r[flag] and r['candidate_bytes_unchanged']
 dst=kit/'evidence'/run;dst.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst/src.name);negatives.append(suffix)
assert json.loads((kit/'normal-hal-audit.json').read_text())['ordinary_hal_cannot_arm_probe']
assert 'PROCESSPAGES probe requires SYSPTES preflight' in (kit/'build-logs/forbidden-entry.log').read_text()
patch=json.loads((kit/'patch-check-0043.json').read_text());assert patch['working_tree_matches_chain']
for log in ['normal-loader.log','hal-normal.log']:
 p=kit/'build-logs'/log
 assert p.exists() and 'FAILED:' not in p.read_text() and 'Build files have been written' in p.read_text()
files=[{'path':p.relative_to(kit/'package').as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((kit/'package').rglob('*')) if p.is_file()]
assert len(files)==33
r={'validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ready_for_physical_upload':True,'installed_on_physical_console':False,'physical_tested':False,'scope':'First process page table and working-set page allocated and zeroed; halt before working-set publication and process initialization.','results':results,'trace_events':1353,'negative_tests':negatives,'package':files,'source_tree':patch['result_tree'],'expected_physical_success':'XWNZ90: First process pages allocated and zeroed.'}
(kit/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('First process pages validated; ready for physical upload.')
