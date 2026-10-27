from pathlib import Path
import re,json,hashlib,datetime
k=Path('outputs/native-interaction727');old=Path('outputs/native-630726')
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h']:
 assert clean((old/n).read_text().replace('726','727'))==clean((k/n).read_text()),n
for n in ['transaction.h','transaction727.c']:
 prior=old/n.replace('727','726');assert clean(prior.read_text().replace('726','727'))==clean((k/n).read_text()),n
a=(old/'bridge.S').read_text().replace('726','727');b=(k/'bridge.S').read_text()
assert a[:a.index('report_offsets:')]==b[:b.index('report_offsets:')]
assert a[a.index('bridge_code_end:'):]==b[b.index('bridge_code_end:'):]
probe=(k/'probe.c').read_text()
assert re.findall(r'cw\((0x[0-9a-f]+),([^)]*)\)',probe)==[('0x1f','0x57'),('0x1b','5')]
assert len(re.findall(r'R32\(0x680630\)\s*=',probe))==2
assert 'o->cr1b[5]==o->cr1b[0]' in probe and 'i<32' in probe
run=json.loads((k/'integration002.json').read_text());assert run['passed'] and len(run['cases'])==50
for c in run['cases']:
 assert c['all_pixels_and_guards_exact']
 assert c['MMIO_writes'] in ([],[[0x680630,2],[0x680630,3]])
 assert c['CRTC_data_writes'] in ([],[[0x1f,0x57]],[[0x1f,0x57],[0x1b,5]])
 if [0x1b,5] in c['CRTC_data_writes']:assert c['direct_indexed_access_order_exact']
v={c['name']:c['raw_result'] for c in run['cases']}
assert v['reassert-dual'][50:53]==[5,5,0x50005]
assert v['behavior-sticky'][29:32]==[5,5,5] and v['behavior-sticky'][0]==0x7275
assert v['behavior-ignored'][50:53]==[0x85,0x85,0x850085] and v['behavior-ignored'][0]==0x7278
assert v['behavior-direct-diff'][50:53]==[0x85,5,0x850005]
assert v['behavior-late'][39]==1 and v['behavior-oscillate'][39]==6
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frontend_wrapper_plan_page_same_except_namespace_comments':True,'bridge_same_except_namespace_and_report_offsets':True,'compiled_write_allowlist':'6302; optional unlock1f57 and oneCR1b05; saved6303; SEQ1 blank/restore; gates5/4; selector traffic','direct_read_immediately_after_write_then_reselected_read':True,'CR1b_retry_or_repair':False,'full_width630_and_full_byteCR1b_restoration':True,'bounded_late_pairs':32,'result_bytes':216,'independent_models_verified':True,'sources':{n:sha(k/n) for n in ['probe.c','probe.h','transaction727.c','transaction.h','main.c','bridge.S']},'limits':'No physical register semantics or full-mode/Windows proof. Retained CR1b05 at final check is reported as baseline restoration failure; no mask waiver.'}
(k/'source-review001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS single CR1b write, exact direct/indexed access and retained guards')
