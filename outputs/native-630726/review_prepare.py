from pathlib import Path
import json,hashlib,struct,datetime
k=Path('outputs/native-630726');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n')
h=load('host002.json');off=[0,0x880,0x8d0,0x8d4,0x5104,0x5180,0x5184,0x5188,0x518c,0x5190,0x5194,0x519c,0x51a8]
b=Path('C:/xwn726/host002/bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','bridge_phase','admission_stage','return_code','630_write_attempts','baseline_pair','after_blanking_pair','after630_2_pair','after630_3_pair','after_output_restore_pair','last_of_32_late_pairs','late_CR1b_changes','summary']
save('optical-schema001.json',{'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'pair_format':'630 full value if <=ffff shifted16, OR full CR1b byte; ffffffff means unrepresentable or unreached, never a valid truncated630','summary':'bit0 cleanup_ok; bit1 selectors_restored; bit2 late_count32 and no changes; bits8..15 late_count; bits16..23 attempts','expected_constant_model':[0x7260000d,4,5,0x726,2,0x30085,0x30085,0x20085,0x30085,0x30085,0x30085,0,0x22007],'expected_coupled_model':[0x7260000d,4,5,0x726,2,0x30085,0x30085,0x20005,0x30085,0x30085,0x30085,0,0x22007],'limits':'Green means completed and final baseline restored; does not select a coupling hypothesis. All samples sequential, not atomic. Late loop changes timing; raw intermediate late pairs not exported.'})
checks=['payload001.json','host002.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration002.json','optical-review001.json','build001.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
assert load('cpu-run001.json')['closed'] and all(v['closed'] for v in load('cpu-run001.json')['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn726/host002')/n)==v,n
for n,v in load('build001.json')['files'].items():assert sha(Path('C:/xwn726/build001')/n)==v['sha256'],n
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':172,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'total_relocations':7,'absolute_relocations':1,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':44,'optical_cases':76,'nxdk_page_cases':20,'nxdk_ownership_cases':372,'host_ownership_cases':131379,'physical_access':False,'failure_retained':'integration001 incorrect harness expectation for CR19 low bit; fresh integration003 / integration002 corrected expectation, binary unchanged','limits':['No physical result yet','No CRTC data writes, encoder/timing programming, writable-mask guess or bit7 waiver','Not full mode-switch or Windows qualification']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build003.py -> build001','active_host':'host_build002.py -> host002','active_cpu':'cpu002.py','active_integration':'integration003.py -> integration002','active_controller':'physical.py','failed_attempt':'integration001 retained'})
print('PASS complete726 pre-stage review and exact source freeze')
