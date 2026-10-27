from pathlib import Path
import json,hashlib,struct,datetime
k=Path('outputs/native-prework737');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n')
h=load('host002.json')
off=[0,0x880,0x8d0,0x8d4,0x51e0,0x5180,0x51c4,0x51d0,0x5194,0x5114,0x5118,0x511c,0x51a8]
b=Path('C:/xwn737/host002/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','bridge_phase','admission_stage','return_code','CPU_work_checksum','baseline_pair','after_unlock_prewrite_pair','first_direct_and_reselected_CR1b','last_of_32_late_pairs','native_CR0','native_CR3','native_CR4','summary']
save('optical-schema001.json',{'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'pair_format':'630 full value if <=ffff shifted16 OR CR1b byte; ffffffff unreached or overflow; full value retained for checks','direct_indexed_format':'first direct byte after4093 register-only iterations shifted16 OR reselected byte; ffffffff unreached','summary':'bit0 full cleanup; bit1 selectors; bit2 late32/nochanges; bit3 work4093/counter0/checksum793a7efe; late count bits8..15;630 attempts bits16..23;CR1b attempt bit24','limits':'Green requires first/reselected05 and final baseline85 restoration. Orange retains failure; decode rows independently. CPU rows are actual native readings; kernel pre-arm context is different. No time calibration or bit7 mask.'})
checks=['payload001.json','host002.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration002.json','optical-review001.json','build001.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
cpu=load('cpu-run001.json');assert cpu['closed'] and all(v['closed'] for v in cpu['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn737/host002')/n)==v,n
for n,v in load('build001.json')['files'].items():assert sha(Path('C:/xwn737/build001')/n)==v['sha256'],n
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':228,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'relocations':len(h['relocations']),'absolute_relocations':len([v for v in h['relocations'] if v['type']=='R_386_32']),'CPU_cases':len(cpu['cases']),'all_CPU_closed':True,'integration_cases':len(load('integration002.json')['cases']),'optical_cases':len(load('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','SingleCR1b05, CPU-only work, no retry/repair/mask','Minimal727 native comparator, not matched full735/736 prefix or mode/Windows qualification']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build003.py -> build001','active_host':'host_build002.py -> host002','active_cpu':'cpu002.py','active_integration':'integration003.py -> integration002','active_controller':'physical.py'})
print('PASS737 pre-stage review and frozen sources')
