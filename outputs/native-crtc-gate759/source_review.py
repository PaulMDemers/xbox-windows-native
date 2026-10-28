"""Compare759 to physical758 transaction and757 frontend; verify expanded initialized bounds."""
from pathlib import Path
import re,json,datetime,hashlib,struct
k=Path(__file__).resolve().parent;old=k.parent/'native-crtc-bit757';kernel=k.parent/'crtc-display-gate758'
def namespace(s,old,new):
 return re.sub(r'(?<![0-9])'+old+r'(?![0-9])',new,re.sub(r'0x'+old+r'(?=[0-9a-f]*\b)','0x'+new,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
a=namespace((kernel/'probe.c').read_text(),'758','759').replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
assert clean(a)==clean((k/'probe.c').read_text())
assert clean(namespace((kernel/'probe.h').read_text(),'758','759'))==clean((k/'probe.h').read_text())
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction759.c','bridge.S']:
 a=namespace((old/n.replace('759','757')).read_text(),'757','759')
 if n=='bridge.S':a=a.replace('0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x533c,0x5348,0x534c','0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x5378,0x5364,0x5370,0x5374')
 assert clean(a)==clean((k/n).read_text()),n
assert 'frequency!=3375000' in (k/'main.c').read_text()
m=json.loads((k/'model001.json').read_text());r=json.loads((k/'integration003.json').read_text());assert m['passed'] and r['passed']
assert len(m['cases'])==169 and len(r['cases'])==159
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==164
 assert all(i in [0,2,3,4,5,0x1f,0x14,0x17,0x19] for i,v in c['CRTC_writes'])
 if c['name'] in ['c17-undo-read','c17-drop-undo']:assert c['raw_result'][0]==0x75917 and c['raw_result'][158]==1 and c['raw_result'][101]==0
 if c['name'] in ['c5b-undo-read','c5b-drop-undo']:assert c['raw_result'][0]==0x75915 and c['raw_result'][148]==1 and c['raw_result'][101]==0
 if c['name'] in ['c3-restore-read','c3-drop-restore']:assert c['raw_result'][0]==0x75913 and c['raw_result'][138]==1 and c['raw_result'][101]==0
 if c['name'] in ['c2-restore-read','c2-drop-restore']:assert c['raw_result'][0]==0x75911 and c['raw_result'][129]==1 and c['raw_result'][101]==0
 if c['name'] in ['c0-restore-read','c0-drop-restore']:assert c['raw_result'][0]==0x759f and c['raw_result'][121]==1 and c['raw_result'][101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='CR1b05-preservation-mismatch')
assert v[:8]==[0x7598,0x7598,11,3,14,0x85,5,15] and v[28:31]==[1,1,0] and v[97]==0
page_checks=[]
for name in ['dual','identity','relocated','scatter']:
 b=(Path('C:/xwn759/host002')/name/'page.bin').read_bytes()
 assert len(b)==32768 and b[0x503c:0x5400]==bytes(0x3c4)
 assert b[0x5400:0x6000]==b'\xa5'*0xc00
 assert 0x5100+164*4==0x5390<0x5400<0x5ffc<0x6000
 assert b[0x6000:]==b'\xa5'*0x2000
 page_checks.append({'layout':name,'request_result_zero_extent':[0x503c,0x5400],'result_extent':[0x5100,0x5390],'guard_extent':[0x5400,0x6000],'stack_extent':[0x6000,0x8000]})
out=k/'source-review001.json';assert not out.exists()
out.write_text(json.dumps({'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches758_except_namespace_native_CPU_guard':True,'frontend_bridge_wrapper_matches757_except_namespace_report_offsets':True,'model_cases':169,'integration_cases':159,'result_bytes':656,'result_end_offset':0x5390,'reserved_result_end':0x5400,'page_bounds':page_checks,'no_CR1b_CR22_CR33_data_writes':True,'cpu_fixture_alias_capture_bytes':73728,'limits':'CR17 before/after/restored and eight aggregate masks exposed. Forward status, selectors, neighbor readbacks and individual prior restorations/H7/nativeCR0/3/4 unexposed. No post-native disk result or full mode/Windows proof.','kernel_evidence_sha256':hashlib.sha256((kernel/'audit001.json').read_bytes()).hexdigest(),'predecessor_failure_sha256':hashlib.sha256((k.parent/'native-crtc-blank751/failure-review001.json').read_bytes()).hexdigest()},indent=2)+'\n',newline='\n')
print('PASS759 source delta, CR17 recovery/report and expanded initialized bounds')
