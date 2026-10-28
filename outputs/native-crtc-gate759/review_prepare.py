"""Freeze759 only after fresh CPU, relocation, pixel and nxdk reviews."""
from pathlib import Path
import json,hashlib,struct,datetime
k=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n',newline='\n')
h=load('host002.json')
off=[0, 2260, 20856, 21136, 21168, 21220, 21252, 21288, 21328, 21368, 21348, 21360, 21364]
b=Path('C:/xwn759/host002/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
assert load('optical-schema001.json')=={'passed': True, 'rows': 13, 'columns': 32, 'bit_order': 'MSB left white1 black0 gray background', 'offsets': [0, 2260, 20856, 21136, 21168, 21220, 21252, 21288, 21328, 21368, 21348, 21360, 21364], 'names': ['signature', 'return_code', 'prefix_cleanup_mask', 'horizontal_cleanup_mask', 'CRTC_cleanup_mask', 'CR00_cleanup_mask', 'CR02_cleanup_mask', 'CR03_cleanup_mask', 'CR05_second_cleanup_mask', 'CR17_cleanup_mask', 'CR17_before', 'CR17_after', 'CR17_restored'], 'CRTC_cleanup_mask': 'bit0 CR04,bit1 CR05; full-byte own-value recovery', 'target_CR17': 99, 'limits': 'Target63 is frozen source contract. Forward status, selectors, CPU, neighbors and individual prior restorations/H7 are not exposed. Eight aggregate recovery masks and CR17 triplet exposed. Final759 requires both forward and recovery success; no raw forward-status observation. No native disk persistence/full mode/Windows proof.'}
checks=['model001.json','payload001.json','host002.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration003.json','optical-review001.json','build002.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
cpu=load('cpu-run001.json');assert cpu['closed'] and len(cpu['cases'])==12 and all(v['closed'] for v in cpu['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn759/host002')/n)==v,n
for n,v in load('build002.json')['files'].items():assert sha(Path('C:/xwn759/build002')/n)==v['sha256'],n
assert len(h['relocations'])==18 and len([v for v in h['relocations'] if v['type']=='R_386_32'])==13
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':656,'result_end':0x5390,'zeroed_reserved_end':0x5400,'stack_start':0x6000,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':len(load('integration003.json')['cases']),'optical_cases':len(load('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','CR17 bit7 clear after qualified prefix/H7/CR04/05/00/02/03 and second CR05','No later horizontal/vertical/pitch/encoder steps','Intentional hold; recovery failure can leave black; watcher/reset required']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build005.py -> build002','active_host':'host_build005.py -> host002','active_cpu':'cpu002.py','active_integration':'integration004.py -> integration003','active_controller':'physical003.py', 'historical_generators_only':['prepare.py','extend_integration.py','prepare_reviews.py']})
print('PASS759 frozen source pre-stage review')
