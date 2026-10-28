"""Independent785 source deltas, complete native cases and new owned memory layout."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-sync-end783';C=K.parent/'vertical-valid-end784'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'784','785')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x5664,0x56dc,0x56c8,0x56d4,0x56d8'
new='0,0x8d4,0x5178,0x5290,0x52b0,0x54b4,0x5514,0x5574,0x56dc,0x5754,0x5740,0x574c,0x5750'
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction785.c','bridge.S']:
 s=ns((O/n.replace('785','783')).read_text(),'783','785')
 if n in ['main.c','page002.c','bridge.S']:s=s.replace('14080','15360')
 if n=='bridge.S':s=s.replace(old,new).replace('0xa5a5a5a5,0x5ffc(%ebp)','0xa5a5a5a5,0x6000(%ebp)')
 if n=='page002.c':s=s.replace('memset(p+0x5000,0,0x740)','memset(p+0x5000,0,0x7b8)').replace('base+0x4800','base+0x5800').replace('at=0x4800+8*i','at=0x5800+8*i')
 assert clean(s)==clean((K/n).read_text()),n
assert 'frequency!=3375000' in (K/'main.c').read_text()
body=(K/'probe.c').read_text();order=['ve','se','sy','vs','vc','vt','v'];addresses=[0x680818,0x680810,0x68080c,0x680814,0x680808,0x680804,0x680800]
positions=[body.index('R32('+hex(a)+')=o->'+n+'_before') for n,a in zip(order,addresses)]+[body.index('gate(4)')];assert positions==sorted(positions)
assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x7|0x07|0x10),',body)
kern=read(C/'audit002.json');assert kern['passed'] and kern['result']['code']==0x784
assert kern['result']['vertical_valid_end']['neighbors_before']==[479,524,479,0,489,492,104,48]
m=read(K/'model001.json');r=read(K/'integration004.json');assert m['passed'] and r['passed'] and len(m['cases'])==536 and len(r['cases'])==526
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==430
 assert all(i in [0,1,2,3,4,5,0x1f,0x14,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
for prefix,off,mask,fwd,undo in [('sy',340,345,0x7852a,0x7852b),('se',370,375,0x7852c,0x7852d),('ve',400,405,0x7852e,0x7852f)]:
 for phase in ['before','after','undo']:
  for j in range(9):
   v=next(c['raw_result'] for c in r['cases'] if c['name']==prefix+'-'+phase+'-'+str(j));assert v[0]==(undo if phase=='undo' else fwd)
   if phase=='undo':assert v[mask]==1<<j and v[101]==0
 for j in range(1,9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']==prefix+'-coupling-'+str(j));assert v[0]==undo and v[mask]==1<<j and v[101]==0
 for f in ['drop-write','wrong-write','drop-undo','wrong-undo']:
  v=next(c['raw_result'] for c in r['cases'] if c['name']==prefix+'-'+f);assert v[0]==(undo if f.endswith('undo') else fwd)
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual');assert all(v[i]==0 for i in masks)
assert v[400:]==[719,479,1,479,719,0,479,479,479,524,524,524,479,479,479,0,0,0,489,489,489,492,492,492,104,104,104,48,48,48]
for field,address,values in [('vertical_writes',0x680800,[479,719]),('vertical_total_writes',0x680804,[524,749]),('vertical_crtc_writes',0x680808,[479,719]),('vertical_valid_start_writes',0x680814,[0]),('vertical_sync_start_writes',0x68080c,[489,724]),('vertical_sync_end_writes',0x680810,[492,729]),('vertical_valid_end_writes',0x680818,[479,719])]:
 assert all(a==address and n in values for c in r['cases'] for a,n in c[field])
h=read(K/'host002.json');pages=[]
for layout in ['dual','identity','relocated','scatter']:
 b=(Path('C:/xwn785/host002')/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x503c:0x57b8]==bytes(0x77c)
 assert b[0x4c00:0x5000]==b'\xa5'*0x400 and b[0x57b8:0x5800]==b'\xa5'*0x48 and b[0x6000:]==b'\xa5'*0x2000
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x5800)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x5800+8*i)==(target&65535,0x10,0x8e00,target>>16)
 assert 0x1000+15360==0x4c00<0x5000<0x503c<0x5100 and 0x5100+430*4==0x57b8<0x5800 and 0x5800+256*8==0x6000
 pages.append({'layout':layout,'payload_extent':[0x1000,0x4c00],'payload_guard':[0x4c00,0x5000],'request':[0x5000,0x503c],'result_extent':[0x5100,0x57b8],'result_guard':[0x57b8,0x5800],'IDT_extent':[0x5800,0x6000],'stack_extent':[0x6000,0x8000],'stack_low_guard':0x6000,'all256IDTentries_exact':True})
offsets=[int(n,0) for n in new.split(',')];b=Path('C:/xwn785/host002/bridge.bin').read_bytes()
assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==offsets
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','vertical_display_end_cleanup_mask','vertical_total_cleanup_mask','vertical_crtc_cleanup_mask','vertical_sync_end_cleanup_mask','vertical_valid_end_cleanup_mask','NVVVALIDEND_before','NVVVALIDEND_after','NVVVALIDEND_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVVALIDSTART','NVVSYNCSTART']
schema={'passed':True,'rows':13,'columns':32,'offsets':offsets,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':20,'target_NVVVALIDEND':479,'limitations':'Same-value CR02 andNVVVALIDSTART drops indistinguishable. Twelve masks andneighbor/CPU/selector values omitted raw; final785 requires all20clear. No native disk/fullmode/Windows proof.'}
for n,obj in [('optical-schema001.json',schema),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches784_except_namespace_native_CPU_guard':True,'frontend_matches783_except_namespace_report_offsets_and_reviewed_layout_changes':True,'result_bytes':1720,'result_end_offset':0x57b8,'page_bounds':pages,'model_cases':536,'integration_cases':526,'failed_recovery_inhibits_output':True,'same_value_drops_indistinguishable':True,'kernel_audit_sha256':sha(C/'audit002.json')})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS785 source delta, optical table, and all new memory boundaries')
