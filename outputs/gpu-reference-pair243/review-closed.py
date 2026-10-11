"""Review actual closed243 paired census, loader pins and cold gates once."""
import ast,hashlib,json
from pathlib import Path
from schema import parse,qualify
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in read(k/'emulator-frozen.json').items():assert sha(ws/p)==h,p
m=read(k/'matrix001.json');state=read(k/'preserve001/host-state.json');t=read(k/'preserve001/trace.json');a=read(k/'preserve001/audit.json');al=read(k/'preserve001/allocation.json')
assert m['closed'] and m['completed'] and state['closed'] and state['audit_exit_code']==0
assert t['passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and t['physical_mode_restored']
assert not t['debugger_memory_writes'] and not t['debugger_register_writes']
assert [e['name'] for e in t['events']]==['actual_xromwell_xbe_entry','actual_freeldr_multiboot_entry']
for e in t['events']:assert e['resident_bytes_match'] and sha(ws/e['pin']['path'])==e['pin']['sha256']
assert t['events'][0]['registers'][8]==0x11100 and t['events'][1]['registers'][8]==0x200a20 and t['events'][1]['registers'][0]==0x2badb002 and not t['events'][1]['registers'][9]&512
p=t['preservation'];result=p['result'];assert result['state']==3 and result['surfaces']==result['dirty']==result['downloaded']==3 and result['bytes']==3072000
assert not any(result[key] for key in ['reason','error','old_halt','consume_stop','consume_words','consume_steps','wait_before','wait_after'])
assert p['closed'] and p['worker_full_byte_comparison_passed'] and p['preservation_scope_passed'] and not p['ram'] and not p['references_retired'] and not p['ownership_qualified']
v=parse(p['paired_inventory_reply']);assert v==p['paired_inventory'] and p['paired_inventory_immutable']
q=qualify(v,t['phase_snapshot']['tuple']);assert q==p['paired_inventory_result']
assert result['request']==result['gate']==t['phase_snapshot']['tuple']['current_fifo'][4:14]
commands=[c['command'] for c in t['monitor']];assert sum(c.startswith('qom-set ') and 'xwn-preserve227 true' in c for c in commands)==1
assert sum(c.endswith('xwn-inventory242-report') for c in commands)==2 and not any(c.startswith(('pmemsave ','memsave ','xp ','write')) for c in commands)
assert not any(c['command'].startswith(('M','X','G','P')) for c in t['gdb_requests'])
assert a['cpu_scope_passed'] and a['observation_scope_passed'] and a['guest_trace_scope_passed'] and a['backend_preservation_scope_passed'] and a['integrity_passed']
assert a['normal_shutdown_count']==1 and a['dashboard_return'] and a['orderly_host_exit_passed']
assert [(r['source'],r['event_id'],r['type']) for r in a['warnings_errors']]==[('Ftdisk',49,1)] and not a['new_events']['application']
assert not any(a[key] for key in ['strict_qualification_passed','ordinary_qualified','physical_qualified','publication_contract_qualified','backend_preservation_qualified'])
assert al['allocation_consistent'] and not al['errors'] and not al['orphan_cluster_count']
f=read(k/'fixture-preserve001.json');control=read(k.parent/'gpu-preserve-entry239/fixture-control001.json');assert f['seed_sha256']==control['seed_sha256'] and f['protected']==control['protected']
assert sha(k/'artifacts/build004/xemu-inventory242.exe')==read(k.parent/'gpu-reference-pair242/build004.json')['executable_sha256']
for py in k.glob('*.py'):ast.parse(py.read_text(encoding='utf-8'))
before,after=v['slots'];s=after['stats'];aliases=[]
for i,row in enumerate(after['textures']):
 for j,surf in enumerate(after['surfaces']):
  for name,offset,n in [('texture',row[0],row[1]),('palette',row[2],row[3])]:
   if n and offset<surf[0]+surf[1] and surf[0]<offset+n:aliases.append(dict(texture=i,surface=j,kind=name,offset=offset,length=n))
observed=dict(callbacks=sum(row[6] for row in after['surfaces']),texture_units=sum(row[0] for row in after['bindings']),texture_cache=s[13],shader_entries=s[15],initialized_shaders=s[39],shader_program_buffers=s[40],shader_save_handles=s[41],module_entries=s[17],element_entries=s[19],display_buffer=s[8],display_dimensions=s[9:11],color_binding=after['context'][18],zeta_binding=after['context'][19],modeled_aliases=aliases)
dest.write_text(json.dumps(dict(passed=True,paired_inventory_scope_passed=True,frozen_pins_unchanged=len(read(k/'emulator-frozen.json')),trace_sha256=sha(k/'preserve001/trace.json'),audit_sha256=sha(k/'preserve001/audit.json'),matrix=m,pair=q,observed=observed,workload=a['workload'],allocation={key:al[key] for key in ['directories','files','directory_clusters','orphan_cluster_count']},compiled_emulator_reused_from='outputs/gpu-reference-pair242/build004.json',strict_qualified=False,ordinary_qualified=False,physical_access=False,native_gpu_ownership=False,limits='Finite modeled reference census; CPU queues/actual GL bindings/all per-object identities/completion unobserved. Save handles not live-thread proof. Shared pixel conversion oracle. Producer admission restored after samples.'),indent=2)+'\n',encoding='utf-8')
print('243 CLOSED paired inventory/preservation/cold scope PASS; strict/native/physical FALSE')
