"""Compare749 to physically qualified744 probe and743 frontend/bridge."""
from pathlib import Path
import re,json,datetime,hashlib
k=Path(__file__).resolve().parent;old=k.parent/'native-crtc-end747';kernel=k.parent/'crtc-total748'
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
a=(kernel/'probe.c').read_text().replace('748','749').replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
assert clean(a)==clean((k/'probe.c').read_text())
assert clean((kernel/'probe.h').read_text().replace('748','749'))==clean((k/'probe.h').read_text())
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction749.c','bridge.S']:
 a=(old/n.replace('749','747')).read_text().replace('747','749')
 if n=='bridge.S':a=a.replace('0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52b4,0x52c0,0x52c8,0x52bc,0x52cc,0x5170,0x512c','0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x52d0,0x52dc,0x52e0,0x5170,0x512c,0x52ec')
 assert clean(a)==clean((k/n).read_text()),n
m=json.loads((k/'model001.json').read_text());r=json.loads((k/'integration003.json').read_text());assert m['passed'] and r['passed']
assert len(m['cases'])==113 and len(r['cases'])==103
for c in r['cases']:
 assert c['all_pixels_and_guards_exact']
 assert all(i in [0,4,5,0x1f,0x14,0x17,0x19] for i,v in c['CRTC_writes'])
 if c['name'] in ['c4-restore-read','c4-restore-write','c5-restore-read','c5-coupling','c5-drop-restore']:
  assert c['raw_result'][0]==0x749c and c['raw_result'][108]!=0 and c['raw_result'][101]==0
for c in r['cases']:
 if c['name'] in ['c0-restore-read','c0-drop-restore']:assert c['raw_result'][0]==0x749f and c['raw_result'][121]==1 and c['raw_result'][101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='CR1b05-preservation-mismatch')
assert v[:8]==[0x7498,0x7498,11,3,14,0x85,5,15] and v[28:31]==[1,1,0] and v[97]==0
out=k/'source-review001.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches748_except_namespace_native_CPU_guard':True,'frontend_bridge_wrapper_matches747_except_namespace_report_offsets':True,'model_cases':113,'integration_cases':103,'result_bytes':496,'result_end_offset':0x52f0,'reserved_result_end':0x5300,'no_CR1b_CR22_CR33_data_writes':True,'cpu_fixture_alias_capture_bytes':73728,'limits':'Native CR00 readback/recovery after qualified prefix/H7/CR04/CR05. Optical CR00 before/after/restored plus CR05after and aggregate masks. CR3/CR4 and individual H7 words not optically exposed. No post-native disk persistence or full mode/Windows proof.','kernel_evidence_sha256':hashlib.sha256((kernel/'audit001.json').read_bytes()).hexdigest()},indent=2)+'\n',newline='\n')
print('PASS749 source delta and CR00 recovery/report contracts')
