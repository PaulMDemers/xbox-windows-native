"""Freeze747 after fresh CPU, relocated integration, optical and nxdk checks."""
from pathlib import Path
import json,hashlib,struct,datetime
k=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n',newline='\n')
h=load('host001.json')
off=[0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52b4,0x52c0,0x52c8,0x52bc,0x52cc,0x5170,0x512c]
b=Path('C:/xwn747/host001/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','return_code','forward_status','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR05_before','CR05_target','CR05_after','CR05_restored','CR04_after_CR05','selectors_restored','native_CR0']
save('optical-schema001.json',{'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'CRTC_cleanup_mask':'bit0 CR04,bit1 CR05; full-byte own-saved-value comparison; nonzero inhibits output enable','target_CR04':93,'target_CR05':62,'limits':'No native CR3/CR4 or individual H7 words displayed. Aggregate results qualify checks only; no post-native disk persistence. No visible480p, fullmode or Windows proof.'})
checks=['model001.json','payload001.json','host001.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration003.json','optical-review001.json','build001.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
cpu=load('cpu-run001.json');assert cpu['closed'] and all(v['closed'] for v in cpu['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn747/host001')/n)==v,n
for n,v in load('build001.json')['files'].items():assert sha(Path('C:/xwn747/build001')/n)==v['sha256'],n
assert len(h['relocations'])==18 and len([v for v in h['relocations'] if v['type']=='R_386_32'])==13
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':464,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'relocations':18,'absolute_relocations':13,'CPU_cases':len(cpu['cases']),'all_CPU_closed':True,'integration_cases':len(load('integration003.json')['cases']),'optical_cases':len(load('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','CR05 low-five-bit write after preserving prefix/H7/CR04','No additional CRTC, vertical, encoder, clock or full-mode replay','Intentional hold; failure can leave black; requires watcher/reset']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build004.py -> build001','active_host':'host_build004.py -> host001','active_cpu':'cpu002.py','active_integration':'integration004.py -> integration003','active_controller':'physical002.py'})
print('PASS747 frozen source pre-stage review')
