"""Independent797 source, execution, memory bounds and optical schema review."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-vblank-end795';C=K.parent/'crtc-vdisplay-high796';P=Path('C:/xwn797/host004')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'796','797')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old=[0,0x8d4]+[0x6440+4*j for j in [30,100,108,435,465,495,525,555,550,553,554]]
new=[0,0x8d4]+[0x6740+4*j for j in [30,100,108,465,495,525,555,585,580,583,584]]
mapping={'21504':'22272','0x5400':'0x5700','0x6400':'0x6700','0x6404':'0x6704','0x643c':'0x673c','0x6440':'0x6740','0x6d50':'0x70c8','0x7000':'0x7100','0x7800':'0x7900'}
for n in ['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction797.c','bridge002.S']:
 s=ns((O/n.replace('797','795')).read_text(),'795','797')
 if n=='bridge002.S':s=s.replace(','.join(hex(i) for i in old[1:]),'OFFSET_PLACEHOLDER')
 s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
 s=s.replace('OFFSET_PLACEHOLDER',','.join(hex(i) for i in new[1:]))
 if n=='page002.c':s=s.replace('memset(p+0x6700,0,0x950)','memset(p+0x6700,0,0x9c8)')
 assert clean(s)==clean((K/n).read_text()),n
assert 'memory.TotalPhysicalPages==16384' in (K/'main004.c').read_text()
assert 'frequency!=3375000' in (K/'main004.c').read_text()
assert '{0xb0000,0x5700}' in (K/'layout004.c').read_text()
body=(K/'probe.c').read_text()
positions=[body.index(t) for t in ['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(7,o->ct7_target)','cw(6,o->ct6_target)','cw(0x16,o->ct16_target)','cw(7,o->cd7_target)','cw(7,o->cd7_before)','cw(0x16,o->ct16_before)','cw(6,o->ct6_before)','cw(7,o->ct7_before)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']]
assert positions==sorted(positions)
assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
assert read(C/'audit001.json')['passed'] and read(C/'closed001.json')['closed']
assert read(O/'audit001.json')['passed'] and read(O/'closed001.json')['closed']
m=read(K/'model001.json');r=read(K/'integration008.json')
assert m['passed'] and r['passed'] and len(m['cases'])==774 and len(r['cases'])==764
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==610
 assert all(i in [0,1,2,3,4,5,6,7,0x10,0x1f,0x14,0x16,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert c['stack_bytes_written_from_top']<=1792 and c['admitted_stack_bytes']==1792
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='cd7-'+phase+'-'+str(j))
  assert v[0]==(0x7973b if phase=='undo' else 0x7973a)
  if phase=='undo':assert v[585]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='cd7-coupling-'+str(j));assert v[0]==0x7973b and v[585]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[580:586]==[116,54,1,54,116,0]
assert v[586:]==[n for x in [12,96,233,207,207,140,255,16] for n in [x,x,x]]
for f in ['drop-write','wrong-write','drop-undo','wrong-undo','wrong-write-drop-undo']:
 v2=next(c['raw_result'] for c in r['cases'] if c['name']=='cd7-'+f)
 assert v2[0]==(0x7973a if f in ['drop-write','wrong-write'] else 0x7973b)
 if f in ['drop-undo','wrong-undo','wrong-write-drop-undo']:assert [v2[i] for i in [585,555,525,495,465,435]]==[1,4,2,0,0,0] and v2[101]==0
h=read(K/'host004.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload006.json')['unpadded_bytes']
assert rawsize==22200 and len(payload)==22272 and payload[rawsize:]==b'\xcc'*(22272-rawsize)
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x673c:0x70c8]==bytes(0x98c)
 assert b[0x70c8:0x7100]==b'\xa5'*56 and b[0x7900:]==b'\xa5'*1792
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x7100)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x7100+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x1000-0x100000)
 assert b[0x1000:0x6700]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x7900,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x1000+22272==0x6700<0x673c<0x6740 and 0x6740+610*4==0x70c8<0x7100 and 0x7100+256*8==0x7900<0x8000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x1000,0x6700],'request':[0x6700,0x673c],'request_guard':[0x673c,0x6740],'result':[0x6740,0x70c8],'result_guard':[0x70c8,0x7100],'IDT':[0x7100,0x7900],'stack':[0x7900,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
b=(P/'bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==new
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR10_cleanup_mask','CR07_total_cleanup_mask','CR06_total_cleanup_mask','CR16_blank_end_cleanup_mask','CR07_display_cleanup_mask','CR07_display_before','CR07_display_after','CR07_display_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND','NVVVALIDEND','CR07sync']
schema={'passed':True,'rows':13,'columns':32,'offsets':new,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':26,'target_CR07_display':54,'limitations':'Same-value CR02/NVVVALIDSTART/CR07total drops indistinguishable. Eighteen masks and neighbor/CPU/selector raw values omitted; final797 requires all26 clear. No native disk/fullmode/Windows proof.'}
stackmax=max(c['stack_bytes_written_from_top'] for c in r['cases'])
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True,'maximum_modeled_stack_bytes_written':stackmax,'stack_allocation_bytes':1792}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches796_except_namespace_native_CPU_guard':True,'frontend_matches795_except_namespace_report_offsets_and_reviewed_layout_changes':True,'result_bytes':2440,'result_end_offset':0x70c8,'page_bounds':pages,'model_cases':774,'integration_cases':764,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit001.json'),'maximum_modeled_stack_bytes_written':stackmax})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS797 source, execution and independent memory-layout review')
