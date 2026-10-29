"""Independent799 source, execution, memory bounds and optical schema review."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-vdisplay-high797';C=K.parent/'crtc-vdisplay-low798';P=Path('C:/xwn799/host004')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'798','799')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old=[0,0x8d4]+[0x6740+4*j for j in [30,100,108,465,495,525,555,585,580,583,584]]
new=[0,0x8d4]+[0x6bc0+4*j for j in [30,100,108,495,525,555,585,615,610,613,614]]
mapping={'22272':'23424','0x5700':'0x5b80','0x6700':'0x6b80','0x6704':'0x6b84','0x673c':'0x6bbc','0x6740':'0x6bc0','0x70c8':'0x75c0','0x7100':'0x7600','0x7900':'0x7e00','0x9c8':'0xa40'}
for n in ['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction799.c','bridge002.S']:
 s=ns((O/n.replace('799','797')).read_text(),'797','799')
 if n=='bridge002.S':s=s.replace(','.join(hex(i) for i in old[1:]),'OFFSET_PLACEHOLDER')
 s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
 s=s.replace('OFFSET_PLACEHOLDER',','.join(hex(i) for i in new[1:]))
 # Length remap above covers request and640 output words.
 assert clean(s)==clean((K/n).read_text()),n
assert 'memory.TotalPhysicalPages==16384' in (K/'main004.c').read_text()
assert 'frequency!=3375000' in (K/'main004.c').read_text()
assert '{0xb0000,0x5b80}' in (K/'layout004.c').read_text()
body=(K/'probe.c').read_text()
positions=[body.index(t) for t in ['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(7,o->ct7_target)','cw(6,o->ct6_target)','cw(0x16,o->ct16_target)','cw(7,o->cd7_target)','cw(0x12,o->cd12_target)','cw(0x12,o->cd12_before)','cw(7,o->cd7_before)','cw(0x16,o->ct16_before)','cw(6,o->ct6_before)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']]
assert positions==sorted(positions)
assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
assert read(C/'audit002.json')['passed'] and read(C/'closed001.json')['closed']
assert read(O/'audit001.json')['passed'] and read(O/'closed001.json')['closed']
m=read(K/'model001.json');r=read(K/'integration008.json')
assert m['passed'] and r['passed'] and len(m['cases'])==814 and len(r['cases'])==804
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==640
 assert all(i in [0,1,2,3,4,5,6,7,0x10,0x12,0x1f,0x14,0x16,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert c['stack_bytes_written_from_top']<=384 and c['admitted_stack_bytes']==512
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='cd12-'+phase+'-'+str(j))
  assert v[0]==(0x7993d if phase=='undo' else 0x7993c)
  if phase=='undo':assert v[615]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='cd12-coupling-'+str(j));assert v[0]==0x7993d and v[615]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[610:616]==[207,223,1,223,207,0]
assert v[616:]==[n for x in [12,54,96,233,207,140,255,16] for n in [x,x,x]]
for f in ['drop-write','wrong-write','drop-undo','wrong-undo','wrong-write-drop-undo']:
 v2=next(c['raw_result'] for c in r['cases'] if c['name']=='cd12-'+f)
 assert v2[0]==(0x7993c if f in ['drop-write','wrong-write'] else 0x7993d)
 if f in ['drop-undo','wrong-undo','wrong-write-drop-undo']:assert [v2[i] for i in [615,585,555,525,495,465,435]]==[1,16,32,16,16,16,16] and v2[101]==0
h=read(K/'host004.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload007.json')['unpadded_bytes']
assert rawsize==23416 and len(payload)==23424 and payload[rawsize:]==b'\xcc'*(23424-rawsize)
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x6bbc:0x75c0]==bytes(0xa04)
 assert b[0x75c0:0x7600]==b'\xa5'*64 and b[0x7e00:]==b'\xa5'*512
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x7600)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x7600+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x1000-0x100000)
 assert b[0x1000:0x6b80]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x7e00,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x1000+23424==0x6b80<0x6bbc<0x6bc0 and 0x6bc0+640*4==0x75c0<0x7600 and 0x7600+256*8==0x7e00<0x8000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x1000,0x6b80],'request':[0x6b80,0x6bbc],'request_guard':[0x6bbc,0x6bc0],'result':[0x6bc0,0x75c0],'result_guard':[0x75c0,0x7600],'IDT':[0x7600,0x7e00],'stack':[0x7e00,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
b=(P/'bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==new
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR07_total_cleanup_mask','CR06_total_cleanup_mask','CR16_blank_end_cleanup_mask','CR07_display_cleanup_mask','CR12_display_cleanup_mask','CR12_display_before','CR12_display_after','CR12_display_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND','NVVVALIDEND','CR07sync','CR10']
schema={'passed':True,'rows':13,'columns':32,'offsets':new,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':27,'target_CR12_display':223,'limitations':'Same-value CR02/NVVVALIDSTART/CR07total drops indistinguishable. Nineteen masks and neighbor/CPU/selector raw values omitted; final799 requires all27 clear. No native disk/fullmode/Windows proof.'}
stackmax=max(c['stack_bytes_written_from_top'] for c in r['cases'])
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True,'maximum_modeled_stack_bytes_written':stackmax,'stack_allocation_bytes':512}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches798_except_namespace_native_CPU_guard':True,'frontend_matches797_except_namespace_report_offsets_and_reviewed_layout_changes':True,'result_bytes':2560,'result_end_offset':0x75c0,'page_bounds':pages,'model_cases':814,'integration_cases':804,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit002.json'),'maximum_modeled_stack_bytes_written':stackmax})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS799 source, execution and independent memory-layout review')
