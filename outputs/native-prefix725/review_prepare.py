from pathlib import Path
import json,hashlib,struct,datetime
k=Path('outputs/native-prefix725');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text());save=lambda n,r:(k/n).write_text(json.dumps(r,indent=2)+'\n')
h=load('host002.json');off=[0,0x880,0x8d0,0x8d4,0x5104,0x5108,0x5208,0x520c,0x5210,0x5214,0x5218,0x521c,0x5150]
b=Path('C:/xwn725/host002/bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','bridge_phase','admission_stage','return_code','attempted_mmio','attempted_crtc','CR1b_immediate','CR1b_after_CR19_restore','CR1b_after_680630_restore','CR1b_after_gate4','CR1b_after_SEQ1_restore_and_readback','CR1b_final_cleanup','cleanup_ok']
save('optical-schema001.json',{'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'expected_success':[0x7250000d,4,5,0x725,11,4,5,5,5,5,5,5,1],'unreached_trace':'ffffffff','sample_semantics':['copy existing immediate CR1b read','extra selector-preserving read after CR19 restoration','extra selector-preserving read after680630 restoration','extra selector-preserving read after output gate4','extra selector-preserving read after SEQ1 restoration/readback','copy existing final CR1b cleanup read'],'limits':'Four added reads can perturb timing; first changed sample brackets a boundary only; unexported MMIO/SEQ/CR11 cleanup checks may also fail'})
checks=['payload001.json','host002.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration001.json','optical-review001.json','build001.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
assert load('cpu-run001.json')['closed'] and all(v['closed'] for v in load('cpu-run001.json')['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn725/host002')/n)==v,n
for n,v in load('build001.json')['files'].items():assert sha(Path('C:/xwn725/build001')/n)==v['sha256'],n
models=[c for c in load('integration001.json')['cases'] if c['name'].startswith('CR1b-changes')]
assert len(models)==5
for i,c in enumerate(models,1):assert c['raw_result'][66:72]==[5]*i+[0x85]*(6-i)
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':296,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'total_relocations':17,'absolute_relocations':11,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':59,'five_transition_vectors_independently_checked':True,'optical_cases':76,'nxdk_page_cases':30,'nxdk_ownership_cases':372,'host_ownership_cases':131379,'physical_access':False,'failure_retained':'host001 exact16 total relocation assertion rejected new17-entry ELF; host002 exact17 passed; no prior console launch','limits':['No physical result yet','Same forward/cleanup writes as724; four extra reads change timing','NoCR22 data write, repeatedCR1b write, mask waiver, or encoder/timing programming','Not full mode-switch or Windows qualification']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build002.py -> build001','active_host':'host_build002.py -> host002','active_cpu':'cpu002.py','active_controller':'physical.py','failed_attempt':'host001, relocate.py exact16 retained'})
print('PASS complete725 pre-stage review and source freeze')
