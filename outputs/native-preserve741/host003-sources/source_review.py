from pathlib import Path
import re,json,datetime
k=Path('outputs/native-preserve741');old=Path('outputs/native-batch738');kernel=Path('outputs/preserve-prefix740')
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
a=(kernel/'probe.c').read_text().replace('740','741').replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
assert clean(a)==clean((k/'probe.c').read_text())
assert clean((kernel/'probe.h').read_text().replace('740','741'))==clean((k/'probe.h').read_text())
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction741.c','bridge.S']:
 a=(old/n.replace('741','738')).read_text().replace('738','741')
 if n=='main.c':a=a.replace('9916,payload_reloc,10,','9916,payload_reloc,8,')
 if n=='page002.c':a=a.replace('count!=10||','count!=8||')
 assert clean(a)==clean((k/n).read_text()),n
m=json.loads((k/'model001.json').read_text());r=json.loads((k/'integration002.json').read_text());assert m['passed'] and r['passed']
assert len(m['cases'])==57 and len(r['cases'])==53
for c in r['cases']:
 assert c['all_pixels_and_guards_exact']
 assert all(i in [0x1f,0x14,0x17,0x19] for i,v in c['CRTC_writes'])
v=next(c['raw_result'] for c in r['cases'] if c['name']=='CR1b05-preservation-mismatch')
assert v[:8]==[0x7418,0x7418,11,3,14,0x85,5,15] and v[28:31]==[1,1,0]
out=k/'source-review001.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches740_except_namespace_header_native_CPU_guard':True,'frontend_bridge_wrapper_matches738_except_namespace_comments_exact8_relocations':True,'model_cases':57,'integration_cases':53,'result_bytes':304,'no_CR1b_CR22_CR33_data_writes':True,'cpu_fixture_alias_capture_bytes':73728,'limits':'No geometry/encoder/full-mode replay; preservation only. No bit7 contract established. CPU fixtures are diskless PC, not physical NV2A.'},indent=2)+'\n')
print('PASS741 source delta and preservation contracts')
