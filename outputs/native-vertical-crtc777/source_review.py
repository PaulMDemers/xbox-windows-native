"""Independent777 source delta, reserved bounds and linked optical schema."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-vertical-total774';C=K.parent/'vertical-crtc776'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'776','777')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x53a4,0x54b4,0x5514,0x5500,0x550c,0x5510'
new='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x54b4,0x5514,0x5574,0x5560,0x556c,0x5570'
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction777.c','bridge.S']:
 s=ns((O/n.replace('777','774')).read_text(),'774','777')
 if n=='bridge.S':s=s.replace(old,new)
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x560)','memset(p+0x5000,0,0x5d8)')
 assert clean(s)==clean((K/n).read_text()),n
assert 'frequency!=3375000' in (K/'main.c').read_text()
read=lambda n:json.loads((K/n).read_text())
m=read('model001.json');r=read('integration004.json');assert m['passed'] and r['passed']
assert len(m['cases'])==379 and len(r['cases'])==369
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==310
 assert all(i in [0,1,2,3,4,5,0x1f,0x14,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert all(a==0x680800 and v in [479,719] for a,v in c['vertical_writes'])
 assert all(a==0x680804 and v in [524,749] for a,v in c['vertical_total_writes'])
 assert all(a==0x680808 and v in [479,719] for a,v in c['vertical_crtc_writes'])
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='vc-'+phase+'-'+str(j))
  assert v[0]==(0x77727 if phase=='undo' else 0x77726)
  if phase=='undo':assert v[285]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='vc-coupling-'+str(j));assert v[0]==0x77727 and v[285]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert v[280:286]==[719,479,1,479,719,0]
assert v[286:]==[479,479,479,524,524,524,724,724,724,729,729,729,0,0,0,719,719,719,104,104,104,48,48,48]
assert all(v[i]==0 for i in masks)
pages=[]
for layout in ['dual','identity','relocated','scatter']:
 b=(Path('C:/xwn777/host002')/layout/'page.bin').read_bytes()
 assert len(b)==32768 and b[0x503c:0x55d8]==bytes(0x59c)
 assert b[0x4700:0x4800]==b'\xa5'*0x100
 assert b[0x55d8:0x6000]==b'\xa5'*0xa28 and b[0x6000:]==b'\xa5'*0x2000
 assert 0x1000+14080==0x4700<0x4800 and 0x4800+256*8==0x5000
 assert 0x5100+310*4==0x55d8<0x5ffc<0x6000
 pages.append({'layout':layout,'payload_extent':[0x1000,0x4700],'IDT_extent':[0x4800,0x5000],'result_extent':[0x5100,0x55d8],'guard_end':0x6000})
offsets=[int(n,0) for n in new.split(',')]
h=read('host002.json');b=Path('C:/xwn777/host002/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==offsets
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','vertical_display_end_cleanup_mask','vertical_total_cleanup_mask','vertical_crtc_cleanup_mask','NVVCRTC_before','NVVCRTC_after','NVVCRTC_restored']
schema={'passed':True,'rows':13,'columns':32,'offsets':offsets,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':['CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13'],'total_masks_required_for_success':16,'target_NVVCRTC':479,'limitations':'Same-value CR02 drops indistinguishable. Eight masks and neighbor/CPU/selector values omitted raw; final777 requires all16 clear. No native disk/fullmode/Windows proof.'}
for n,obj in [('optical-schema001.json',schema),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches776_except_namespace_native_CPU_guard':True,'frontend_matches774_except_namespace_report_offsets_result_extent':True,'result_bytes':1240,'result_end_offset':0x55d8,'page_bounds':pages,'model_cases':379,'integration_cases':369,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit001.json')})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS777 source delta, optical table and reserved memory boundaries')
