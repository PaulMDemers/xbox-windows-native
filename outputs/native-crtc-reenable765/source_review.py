"""Independent765 source delta, expanded result bounds and report checks."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-crtc-repeat763';C=K.parent/'crtc-reenable764'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)', '0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'764','765')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
oldoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5378,0x53a4,0x53d4,0x53c0,0x53cc,0x53d0'
newoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x53d4,0x5404,0x53f0,0x53fc,0x5400'
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction765.c','bridge.S']:
 s=ns((O/n.replace('765','763')).read_text(),'763','765')
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x400)','memset(p+0x5000,0,0x500)')
 if n=='bridge.S':s=s.replace(oldoff,newoff)
 assert clean(s)==clean((K/n).read_text()),n
assert 'frequency!=3375000' in (K/'main.c').read_text()
read=lambda n:json.loads((K/n).read_text())
m=read('model001.json');r=read('integration003.json');assert m['passed'] and r['passed']
assert len(m['cases'])==228 and len(r['cases'])==218
for v in r['cases']:
 assert v['all_pixels_and_guards_exact'] and len(v['raw_result'])==200
 assert all(i in [0,1,2,3,4,5,0x1f,0x14,0x17,0x19] for i,x in v['CRTC_writes'])
for name in ['c2b-undo-read','c2b-wrong-write-drop-undo']:
 v=next(c['raw_result'] for c in r['cases'] if c['name']==name)
 assert v[0]==0x7651b and v[181]==1 and v[101]==0
for name in ['c2b-drop-write','c2b-drop-undo']:
 v=next(c['raw_result'] for c in r['cases'] if c['name']==name)
 assert v[0]==v[1]==0x765 and v[176:182]==[89,89,1,89,89,0]
for name in ['c17b-undo-read','c17b-drop-undo']:
 v=next(c['raw_result'] for c in r['cases'] if c['name']==name)
 assert v[0]==0x7651d and v[193]==1 and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert v[188:194]==[99,227,1,227,99,0] and v[194:200]==[92,89,89,128,93,190]
pages=[]
for layout in ['dual','identity','relocated','scatter']:
 b=(Path('C:/xwn765/host002')/layout/'page.bin').read_bytes()
 assert len(b)==32768 and b[0x503c:0x5500]==bytes(0x4c4)
 assert b[0x5500:0x6000]==b'\xa5'*0xb00 and b[0x6000:]==b'\xa5'*0x2000
 assert 0x5100+200*4==0x5420<0x5500<0x5ffc<0x6000
 pages.append({'layout':layout,'result_extent':[0x5100,0x5420],'initialized_end':0x5500,'guard_end':0x6000})
offsets=[int(n,0) for n in newoff.split(',')]
host=read('host002.json');b=Path('C:/xwn765/host002/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,host['bridge_symbols']['report_offsets']))==offsets
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','CR01_cleanup_mask','CR02_second_cleanup_mask','CR17_second_cleanup_mask','CR17_second_before','CR17_second_after','CR17_second_restored']
schema={'passed':True,'rows':13,'columns':32,'offsets':offsets,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':['CR03','secondCR05','firstCR17'],'total_masks_required_for_success':11,'target_CR17_second':227,'limitations':'Same-value59 write/undo drops cannot be distinguished by unchanged readback. Forward status, selectors, CPU, neighbors and prior individual restorations unexposed. Final765 requires all eleven masks clear. No native disk/fullmode/Windows proof.'}
for n,obj in [('optical-schema001.json',schema),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches764_except_namespace_native_CPU_guard':True,'frontend_matches763_except_namespace_report_offsets_initialization':True,'result_bytes':800,'result_end_offset':0x5420,'page_bounds':pages,'model_cases':228,'integration_cases':218,'same_value_negative_controls_honestly_indistinguishable':True,'wrong_value_failed_undo_detected_output_inhibited':True,'kernel_audit_sha256':sha(C/'audit001.json')})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n',newline='\n')
print('PASS765 independent delta, report, same-value limits and bounds')
