"""Review actual closed236 pins, executing entries and separate qualification scopes."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import capstone
from parsing import span,journal_ack,after_write_instruction
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=read(k/'trace001/host-state.json');t=read(k/'trace001/trace.json');a=read(k/'trace001/audit.json');alloc=read(k/'trace001/allocation.json');inv=read(k/'inventory001.json')
assert h['closed'] and h['cleanup_record_exists'] and h['runner_exit_code']==h['tracer_exit_code']==h['observer_exit_code']==h['audit_exit_code']==0
assert t['passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints']
assert t['physical_mode_restored'] and t['prior_physical_mode']=='0' and not t['debugger_memory_writes'] and not t['debugger_register_writes']
frozen=read(k/'emulator-frozen.json')
for name,digest in frozen.items():assert sha(ws/name)==digest,name
assert read(k/'connection-test001.json')['source_sha256']==sha(k/'supervise-emulator.py')
assert read(k/'guard-test001.json')['source_sha256']==sha(k/'trace.py')
assert read(k/'parsing-test003.json')['source_sha256']==sha(k/'parsing.py')
events=t['events'];assert [v['name'] for v in events]==['guest_irq_write_completed','actual_xromwell_xbe_entry','actual_freeldr_multiboot_entry']
pins=[]
for row in events:
 for name,pin in row.items():
  if name.endswith('_pin') or name=='pin':
   p=ws/pin['path'];assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes'];pins.append(pin)
writer=events[0];code=(ws/writer['code_pin']['path']).read_bytes()
assert code==span((k/'artifacts/inputs/dashboard.xbe').read_bytes(),inv['dashboard'],writer['code_pin']['address'],64)
decoded=after_write_instruction(code,writer['code_pin']['address'],writer['post_write_eip'],writer['registers'],capstone);assert decoded==writer['writer_candidates'] and len(decoded)==1
ack=journal_ack(t['wait_irq_snapshot']['reply'],decoded[0]['value']);assert ack==t['completed_write_corroboration']
xe,fe=events[1:];xb=(ws/xe['pin']['path']).read_bytes();fb=(ws/fe['pin']['path']).read_bytes()
assert xe['registers'][8]==inv['launcher']['entry'] and xb==span((k/'artifacts/inputs/xromwell.xbe').read_bytes(),inv['launcher'],xe['registers'][8],32)
entry=int(inv['freeldr']['entry_address'],16);offset=entry-int(inv['freeldr']['staging_address'],16)
assert fe['registers'][8]==entry and fb==(k/'artifacts/inputs/freeldr.sys').read_bytes()[offset:offset+32]
assert fe['registers'][0]==0x2badb002 and not fe['registers'][9]&0x200
commands=[v['command'] for v in t['gdb_requests']]
for kind,address,size in [(2,0xfd400100,4),(0,xe['registers'][8],1),(0,entry,1)]:
 assert commands.count(f'Z{kind},{address:x},{size:x}')==commands.count(f'z{kind},{address:x},{size:x}')==1
assert sum(v['command'].endswith(' xwn-snapshot234 true') for v in t['monitor'])==1
assert not any('xwn-preserve232 true' in v['command'] for v in t['monitor'])
launch=read(k/'trace001/launch.json');assert len(launch['cycles'])==1 and launch['cycles'][0]['status']=='accepted' and launch['cycles'][0]['dashboard_return']
assert a['cpu_scope_passed'] and a['guest_trace_scope_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
assert not a['strict_qualification_passed'] and not a['backend_preservation_qualified'] and not a['ordinary_qualified']
assert [(v['source'],v['event_id'],v['type']) for v in a['warnings_errors']]==[('Ftdisk',49,1)]
assert not a['new_events']['application'] and alloc['allocation_consistent'] and not alloc['errors'] and not alloc['orphan_cluster_count']
dest.write_text(json.dumps(dict(passed=True,frozen_pins_unchanged=len(frozen),resident_pins=pins,actual_executing_entries_match=True,writer_boundary_reconstructed=True,writer=decoded[0],last_ack_before=ack['ack_before'],last_ack_after=ack['ack_after'],freeldr_multiboot_magic=fe['registers'][0],freeldr_cpu_interrupts_disabled=True,debugger_teardown=True,no_gpu_ownership_qualified=True,cold_integrity=True,normal_shutdown_count=1,strict_events_passed=False,actual_strict_failures=[dict(source=v['source'],event_id=v['event_id'],type=v['type']) for v in a['warnings_errors']],host_process_forced_exit=True,all_file_content_and_cache_flush_safety_qualified=False,physical_access=False,trace_sha256=sha(k/'trace001/trace.json'),audit_sha256=sha(k/'trace001/audit.json'),source_sha256=sha(Path(__file__))),indent=2)+'\n')
print('236 actual evidence/source review PASS')
