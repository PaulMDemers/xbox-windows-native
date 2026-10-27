"""Compare743 with closed742 probe and741 bridge/frontend source, not runtimes."""
from pathlib import Path
import re,json,datetime,hashlib
k=Path(__file__).resolve().parent;old=k.parent/'native-preserve741';kernel=k.parent/'horizontal-prefix742'
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
a=(kernel/'probe.c').read_text().replace('742','743').replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
assert clean(a)==clean((k/'probe.c').read_text())
assert clean((kernel/'probe.h').read_text().replace('742','743'))==clean((k/'probe.h').read_text())
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction743.c','bridge.S']:
 a=(old/n.replace('743','741')).read_text().replace('741','743')
 if n=='main.c':a=a.replace('9916,payload_reloc,8,','9916,payload_reloc,13,')
 if n=='page002.c':a=a.replace('count!=8||','count!=13||')
 if n=='bridge.S':a=a.replace('0,0x880,0x8d4,0x5104,0x5110,0x5114,0x5118,0x5178,0x5170,0x512c,0x5130,0x5134,0x511c','0,0x880,0x8d4,0x5104,0x5110,0x528c,0x5178,0x5290,0x5170,0x512c,0x5130,0x5134,0x5288')
 assert clean(a)==clean((k/n).read_text()),n
m=json.loads((k/'model001.json').read_text());r=json.loads((k/'integration002.json').read_text());assert m['passed'] and r['passed']
assert len(m['cases'])==89 and len(r['cases'])==79
for c in r['cases']:
 assert c['all_pixels_and_guards_exact']
 assert all(i in [0x1f,0x14,0x17,0x19] for i,v in c['CRTC_writes'])
v=next(c['raw_result'] for c in r['cases'] if c['name']=='CR1b05-preservation-mismatch')
assert v[:8]==[0x7438,0x7438,11,3,14,0x85,5,15] and v[28:31]==[1,1,0] and v[97]==0
for c in r['cases']:
 if c['name'].startswith(('horizontal-restore-','horizontal-cleanup-')):assert c['raw_result'][0]==0x743a and c['raw_result'][100]!=0 and c['raw_result'][101]==0
out=k/'source-review001.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches742_except_namespace_comments_native_CPU_guard':True,'frontend_bridge_wrapper_matches741_except_namespace_comments_13_relocations_report_offsets':True,'model_cases':89,'integration_cases':79,'result_bytes':416,'result_end_offset':0x52a0,'reserved_result_end':0x5300,'no_CR1b_CR22_CR33_data_writes':True,'cpu_fixture_alias_capture_bytes':73728,'limits':'Native horizontal-only readback and recovery. No vertical/encoder/full-mode replay. Optical summary omits individual timing words; no disk persistence after native handoff.','kernel_evidence_sha256':hashlib.sha256((kernel/'audit001.json').read_bytes()).hexdigest()},indent=2)+'\n')
print('PASS743 source delta, horizontal recovery and report contracts')
