"""Freeze native743 after fresh CPU, integration, optical and nxdk validation."""
from pathlib import Path
import json,hashlib,struct,datetime
k=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n')
h=load('host001.json')
off=[0,0x880,0x8d4,0x5104,0x5110,0x528c,0x5178,0x5290,0x5170,0x512c,0x5130,0x5134,0x5288]
b=Path('C:/xwn743/host001/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','bridge_phase','return_code','forward_status','prefix_first_mismatch','horizontal_first_mismatch','prefix_cleanup_mask','horizontal_cleanup_mask','selectors_restored','native_CR0','native_CR3','native_CR4','horizontal_checks_completed']
save('optical-schema001.json',{'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'prefix_cleanup_mask':'20 original full-value comparisons; bit15 also set when horizontal failure deliberately leaves SEQ1 blank','horizontal_cleanup_mask':'bits0..6 in original seven-word order; zero means own saved-value recovery matched before enable','first_mismatch':'ffffffff means no mismatch recorded; use phase/return/forward/checkcount to distinguish refusal','limits':'Summary only; individual native timing words and expected/observed mismatch bytes are not displayed or disk-persisted. Kernel742 raw words cannot substitute. No visible480p, encoder/full-mode or Windows proof.'})
checks=['model001.json','payload001.json','host001.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration002.json','optical-review001.json','build001.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
cpu=load('cpu-run001.json');assert cpu['closed'] and all(v['closed'] for v in cpu['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn743/host001')/n)==v,n
for n,v in load('build001.json')['files'].items():assert sha(Path('C:/xwn743/build001')/n)==v['sha256'],n
assert len(h['relocations'])==18 and len([v for v in h['relocations'] if v['type']=='R_386_32'])==13
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':416,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'relocations':18,'absolute_relocations':13,'CPU_cases':len(cpu['cases']),'all_CPU_closed':True,'integration_cases':len(load('integration002.json')['cases']),'optical_cases':len(load('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Preserving prefix then seven horizontal timing words and own-value recovery','No vertical/encoder/full-mode replay or Windows','Intentional native hold; failed restoration can leave output black; requires watcher and manual reset']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build003.py -> build001','active_host':'host_build004.py -> host001','active_cpu':'cpu002.py','active_integration':'integration003.py -> integration002','active_controller':'physical002.py'})
print('PASS743 pre-stage review and frozen sources')
