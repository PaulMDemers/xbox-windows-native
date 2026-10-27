from pathlib import Path
import json,hashlib,struct,datetime
k=Path('outputs/native-preserve741');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((k/n).read_text())
def save(n,r):
 assert not (k/n).exists();(k/n).write_text(json.dumps(r,indent=2)+'\n')
h=load('host003.json')
off=[0,0x880,0x8d4,0x5104,0x5110,0x5114,0x5118,0x5178,0x5170,0x512c,0x5130,0x5134,0x511c]
b=Path('C:/xwn741/host003/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off
names=['signature','bridge_phase','return_code','forward_status','first_mismatch_zero_based','expected','observed','cleanup_mask','selectors_restored','native_CR0','native_CR3','native_CR4','checks_completed']
save('optical-schema001.json',{'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'cleanup_mask':'bits0..10 MMIO in setup order;11..14 CR14/17/19/1b;15SEQ1;16CR11;17GR04;18CR22;19CR33;0 means all saved-value cleanup comparisons passed','first_mismatch':'0..10 MMIO,11..14 CR14/17/19/1b;ffffffff no forward mismatch recorded, including preflight refusal; use code/phase/checkcount to interpret','limits':'Full32-bit raw expected/observed; no truncation/mask. Kernel pre-arm context is separate from native CR0/3/4. Stops before CR22/CR33 writes, geometry and encoder programming. No original full-mode failure attribution.'})

checks=['model001.json','payload001.json','host003.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration002.json','optical-review001.json','build001.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert load(n)['passed'],n
cpu=load('cpu-run001.json');assert cpu['closed'] and all(v['closed'] for v in cpu['cases'])
for n,v in h['sources'].items():assert sha(k/n)==v,n
for n,v in h['files'].items():assert sha(Path('C:/xwn741/host003')/n)==v,n
for n,v in load('build001.json')['files'].items():assert sha(Path('C:/xwn741/build001')/n)==v['sha256'],n
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(k/n) for n in checks},'result_bytes':304,'payload_bytes':load('payload001.json')['unpadded_bytes'],'padded_payload_extent':9916,'relocations':len(h['relocations']),'absolute_relocations':len([v for v in h['relocations'] if v['type']=='R_386_32']),'CPU_cases':len(cpu['cases']),'all_CPU_closed':True,'integration_cases':len(load('integration002.json')['cases']),'optical_cases':len(load('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Eleven MMIO/three CRTC writes; full saved CR1b check; no CR1b/CR22/CR33 writes','740 preservation sequence matched with native CPU guard; no extra delay, retry, repair or mask','Not original full704 mode replay, Windows or timing qualification']})
save('sources001.json',{'files':{p.name:sha(p) for p in k.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build003.py -> build001','active_host':'host_build003.py -> host003','active_cpu':'cpu002.py','active_integration':'integration003.py -> integration002','active_controller':'physical.py'})
print('PASS741 pre-stage review and frozen sources')
