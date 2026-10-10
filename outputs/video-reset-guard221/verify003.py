"""Independent raw guard/paired-return review of the CLOSED corrected002 pair."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'pair-verification003.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in read(k/'frozen.json').items():assert sha(ws/name)==digest,('Historical001 pin changed',name)
for name,digest in read(k/'frozen002.json').items():assert sha(ws/name)==digest,('Corrected002 pin changed',name)
# Separate construction by 256-byte blocks, equivalent pattern specification.
expected=b''.join(bytes(((low*73+block*19+0x5b)&255) for low in range(256)) for block in range(336))
assert len(expected)==84*1024
r={'scope':__doc__,'physical_access':False,'ordinary_qualified':False,'gpu_context_qualified':False,'cases':{},'pins':{},'passed':False}
for case in ['control002','candidate002']:
 out=k/case;trace=read(out/'trace.json');audit=read(out/'audit.json');host=read(out/'host-state.json');launch=read(out/'launch.json')
 assert host['closed'] and all(host[n]==0 for n in ['runner_exit','tracer_exit','supervisor_exit','audit_exit'])
 assert trace['passed'] and trace['closed'] and trace['guest_resumed'] and not trace['remaining_breakpoints'] and not trace.get('breakpoint_cleanup_errors')
 assert audit['guard_scope_passed'] and audit['integrity_passed'] and audit['normal_shutdown_count']==0 and not audit['ordinary_qualified'] and not audit['dump_qualified']
 assert launch['status']=='single_crash_closed_pending_cold_audit'
 assert trace['events'][0]['kind']=='bugcheck_entry' and trace['events'][0]['arguments']==[0xe058d221,0x44554d50,0x221,0x10000,1]
 assert trace['events'][-1]['kind']=='crash_text_complete_before_callbacks'
 expected_stages=['seeded_at_intended_bugcheck','private_reset_return','public_reset_return','crash_text_complete']
 assert [v['stage'] for v in trace['guard_checks']]==expected_stages
 guards=[]
 for index,v in enumerate(trace['guard_checks']):
  p=out/'artifacts'/v['raw_guard_path'];raw=p.read_bytes();assert len(raw)==len(expected) and sha(p)==v['tail_sha256']
  saved=out/'artifacts'/v['raw_saved_row_path'];sr=saved.read_bytes();assert len(sr)==8960 and sha(saved)==v['saved_row_sha256']
  match=raw==expected;zero=raw==bytes(len(expected));assert match==v['guard_equal'] and zero==v['zero_tail']
  if index==0 or case=='candidate002':assert match
  elif index in [1,2]:assert zero
  else:assert not match # Control destruction; final rendering need not retain zero.
  if index in [1,2]:assert sr==bytes(8960),'Saved row not zero at reset return'
  # Final saved-row contents are observations, not excluded-tail protection.
  distribution={str(value):raw.count(value) for value in sorted(set(raw))}
  saved_distribution={str(value):sr.count(value) for value in sorted(set(sr))}
  assert v['state']==trace['before_seed']
  guards.append({'stage':v['stage'],'bytes':len(raw),'matched':match,'zero':zero,'raw_sha256':sha(p),'saved_row_bytes':len(sr),'saved_row_sha256':sha(saved),'byte_distribution':distribution,'saved_row_distribution':saved_distribution})
 returns={e['function']:e for e in trace['events'] if e.get('kind')=='render_return'}
 entries={e['function']:e for e in trace['events'] if e.get('kind')=='render_entry'}
 for n,delta in [('ResetDisplay',4),('VidResetDisplay',4),('VidSolidColorFill',24),('VidDisplayString',8)]:
  a,b=entries[n],returns[n];assert a['thread']==b['thread'] and b['registers']['ESP']==a['registers']['ESP']+delta
 assert entries['ResetDisplay']['argument_words'][0]==0,'This protocol covers actual NT5 crash SetMode FALSE only'
 assert entries['ResetDisplay']['irql']==31
 frame=trace['before_seed']['globals']['_FrameBufferStart'];back=trace['before_seed']['globals']['_BackBuffer'];end=trace['indexed_end'];tail=trace['tail_start']
 assert tail==frame+0x3eb000 and end==back+316160
 assert end==(tail if case=='candidate002' else frame+0x400000)
 assert trace['tail_mapping']['physical_start']==0x03feb000 and len(trace['tail_mapping']['ptes'])==21
 for i,pte in enumerate(trace['tail_mapping']['ptes']):assert pte&1 and pte&16 and (pte&0xfffff000)==0x03feb000+i*4096
 r['cases'][case]={'guards':guards,'entries_returns':4,'actual_reset_setmode':0,'actual_reset_irql':31,'indexed_end':end,'tail_start':tail,'cold_integrity':True,'normal_shutdown_count':0,'crash_disk_sha256':audit['crash_disk_sha256']}
 for name in ['trace.json','audit.json','closure.json','host-state.json','launch.json']:r['pins'][case+'/'+name]=sha(out/name)
old=read(k/'control001/trace.json');assert not old['passed'] and 'VidResetDisplay' in old['error'] and old['closed'] and not old['remaining_breakpoints'] and old['guest_resumed']
assert not (k/'candidate001/runner-start.json').exists(),'Unused original candidate must remain NEVER launched'
failure=read(k/'posthoc002-failure.json');assert failure['original_preserved'] and not failure['candidate_evaluated'] and failure['returncode']!=0
r['posthoc002_failure_sha256']=sha(k/'posthoc002-failure.json')
r.update(passed=True,original_abi_failure_preserved=True,candidate001_never_launched=True,full_raw_guard_bytes_verified=4*2*84*1024,source_sha256=sha(Path(__file__)),limits='Actual IRQL31 crash SetMode FALSE reset/fill/string only. Host-seeded tail, no SetMode TRUE initial boot guard, GPU context/cache/commands, physical promotion or dump recovery. Selected file hashes/hive structures/allocation are not all file content.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Corrected002 raw guards and exact reset pairs PASS')
