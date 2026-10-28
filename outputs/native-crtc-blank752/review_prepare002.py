"""Freeze752 only after fresh CPU, relocation, pixel and nxdk reviews."""
from pathlib import Path
import json,hashlib,struct,datetime
k=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n',newline='\n')
h=load('host001.json')
off=[0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x52f0,0x52fc,0x5300,0x5170,0x512c]
b=Path('C:/xwn752/host001/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','return_code','forward_status','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','CR02_before','CR02_after','CR02_restored','selectors_restored','native_CR0']
assert load('optical-schema001.json')=={'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'CRTC_cleanup_mask':'bit0 CR04,bit1 CR05; full-byte own-value recovery','target_CR02':89,'limits':'Target59 is frozen source contract. CR00/04/05 neighbor readbacks and individual restorations/H7/CR3/CR4 are not exposed. Five aggregate recovery masks exposed. No native disk persistence/full mode/Windows proof.'}
checks=['model001.json','payload001.json','host001.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration003.json','optical-review001.json','build002.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
cpu=load('cpu-run001.json');assert cpu['closed'] and len(cpu['cases'])==12 and all(v['closed'] for v in cpu['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn752/host001')/n)==v,n
for n,v in load('build002.json')['files'].items():assert sha(Path('C:/xwn752/build002')/n)==v['sha256'],n
assert len(h['relocations'])==18 and len([v for v in h['relocations'] if v['type']=='R_386_32'])==13
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':532,'result_end':0x5314,'zeroed_reserved_end':0x5400,'stack_start':0x6000,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':len(load('integration003.json')['cases']),'optical_cases':len(load('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','CR02 after qualified prefix/H7/CR04/05/00','No later horizontal/vertical/pitch/encoder steps','Intentional hold; recovery failure can leave black; watcher/reset required']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build005.py -> build002','active_host':'host_build004.py -> host001','active_cpu':'cpu002.py','active_integration':'integration004.py -> integration003','active_controller':'physical003.py','historical_generators_only':['seed_prepare.py','seed_extend_integration.py']})
print('PASS752 frozen source pre-stage review')
