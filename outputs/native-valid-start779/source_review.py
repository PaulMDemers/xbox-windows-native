"""Independent779 source delta, reserved bounds and linked optical schema."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-vertical-crtc777';C=K.parent/'vertical-valid-start778'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'778','779')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x54b4,0x5514,0x5574,0x5560,0x556c,0x5570'
new='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x55ec,0x55dc,0x55d8,0x55e4,0x55e8'
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction779.c','bridge.S']:
 s=ns((O/n.replace('779','777')).read_text(),'777','779')
 if n=='bridge.S':s=s.replace(old,new)
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x5d8)','memset(p+0x5000,0,0x650)')
 assert clean(s)==clean((K/n).read_text()),n
assert 'frequency!=3375000' in (K/'main.c').read_text()
body=(K/'probe.c').read_text()
assert body.index('R32(0x680814)=o->vs_before')<body.index('R32(0x680808)=o->vc_before')<body.index('R32(0x680804)=o->vt_before')<body.index('R32(0x680800)=o->v_before')<body.index('gate(4)')
assert not re.search(r'R32\(0x680(?:80c|810|818)\)\s*=',body)
assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
kern=json.loads((C/'audit002.json').read_text());assert kern['passed'] and kern['result']['code']==0x778
assert kern['result']['vertical_valid_start']['neighbors_before']==[479,524,479,724,729,719,104,48]
read=lambda n:json.loads((K/n).read_text())
m=read('model001.json');r=read('integration004.json');assert m['passed'] and r['passed']
assert len(m['cases'])==419 and len(r['cases'])==409
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==340
 assert all(i in [0,1,2,3,4,5,0x1f,0x14,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert all(a==0x680800 and v in [479,719] for a,v in c['vertical_writes'])
 assert all(a==0x680804 and v in [524,749] for a,v in c['vertical_total_writes'])
 assert all(a==0x680808 and v in [479,719] for a,v in c['vertical_crtc_writes'])
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='vs-'+phase+'-'+str(j))
  assert v[0]==(0x77929 if phase=='undo' else 0x77928)
  if phase=='undo':assert v[315]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='vs-coupling-'+str(j));assert v[0]==0x77929 and v[315]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert v[310:]==[0,0,1,0,0,0,479,479,479,524,524,524,479,479,479,724,724,724,729,729,729,719,719,719,104,104,104,48,48,48]
assert all(v[i]==0 for i in masks)
for name in ['vs-drop-write','vs-drop-undo']:
 c=next(c for c in r['cases'] if c['name']==name);assert c['raw_result']==v
bad=next(c['raw_result'] for c in r['cases'] if c['name']=='vs-wrong-write-drop-undo');assert bad[0]==0x77929 and bad[315]==1 and bad[285]==32
assert all(a==0x680814 and n==0 for c in r['cases'] for a,n in c['vertical_valid_start_writes'])
pages=[]
for layout in ['dual','identity','relocated','scatter']:
 b=(Path('C:/xwn779/host002')/layout/'page.bin').read_bytes()
 assert len(b)==32768 and b[0x503c:0x5650]==bytes(0x614)
 assert b[0x4700:0x4800]==b'\xa5'*0x100
 assert b[0x5650:0x6000]==b'\xa5'*0x9b0 and b[0x6000:]==b'\xa5'*0x2000
 assert 0x1000+14080==0x4700<0x4800 and 0x4800+256*8==0x5000
 assert 0x5100+340*4==0x5650<0x5ffc<0x6000
 pages.append({'layout':layout,'payload_extent':[0x1000,0x4700],'IDT_extent':[0x4800,0x5000],'result_extent':[0x5100,0x5650],'guard_end':0x6000})
offsets=[int(n,0) for n in new.split(',')]
h=read('host002.json');b=Path('C:/xwn779/host002/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==offsets
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','vertical_display_end_cleanup_mask','vertical_total_cleanup_mask','vertical_crtc_cleanup_mask','vertical_valid_start_cleanup_mask','NVVVALIDSTART_target','NVVVALIDSTART_before','NVVVALIDSTART_after','NVVVALIDSTART_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13']
schema={'passed':True,'rows':13,'columns':32,'offsets':offsets,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':17,'target_NVVVALIDSTART':0,'limitations':'Same-value CR02 andNVVVALIDSTART drops indistinguishable. Ten masks andneighbor/CPU/selector values omitted raw; final779 requires all17clear. No native disk/fullmode/Windows proof.'}
for n,obj in [('optical-schema001.json',schema),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches778_except_namespace_native_CPU_guard':True,'frontend_matches777_except_namespace_report_offsets_result_extent':True,'result_bytes':1360,'result_end_offset':0x5650,'page_bounds':pages,'model_cases':419,'integration_cases':409,'failed_recovery_inhibits_output':True,'same_value_drops_indistinguishable':True,'kernel_audit_sha256':sha(C/'audit002.json')})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS779 source delta, optical table and reserved memory boundaries')
