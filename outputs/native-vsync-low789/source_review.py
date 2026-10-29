"""Independent789 source delta, result layout, stack bounds and optical semantics."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-vsync-high787';C=K.parent/'crtc-vsync-low788';P=Path('C:/xwn789/host003')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
for n in ['probe.c','probe.h']:
 s=ns((C/n).read_text(),'788','789')
 if n=='probe.c':s=s.replace('(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)','(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)')
 assert clean(s)==clean((K/n).read_text()),n
old=[0,0x8d4,0x50b8,0x51d0,0x51f0,0x53f4,0x5454,0x54b4,0x5694,0x570c,0x56f8,0x5704,0x5708]
new=[0,0x8d4,0x58b8,0x59d0,0x59f0,0x5bf4,0x5c54,0x5cb4,0x5f0c,0x5f84,0x5f70,0x5f7c,0x5f80]
remapping={'16384':'18432','0x5000':'0x5800','0x5004':'0x5804','0x503c':'0x583c','0x5040':'0x5840','0x5770':'0x5fe8','0x5800':'0x6000','0x6000':'0x6800','0x6004':'0x6804','0x770':'0x7e8'}
for n in ['main.c','layout.c','layout.h','plan.c','plan.h','page002.c','page.h','transaction.h','transaction789.c','bridge.S']:
 s=ns((O/n.replace('789','787')).read_text(),'787','789')
 if n=='bridge.S':s=s.replace(','.join(hex(i) for i in old[1:]),','.join(hex(i) for i in new[1:]))
 s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,remapping))+r')(?![0-9a-zA-Z])',lambda m:remapping[m[0]],s)
 assert clean(s)==clean((K/n).read_text()),n
assert 'frequency!=3375000' in (K/'main.c').read_text()
body=(K/'probe.c').read_text()
positions=[body.index(t) for t in ['cw(7,o->c7_target)','cw(0x10,o->c10_target)','cw(0x10,o->c10_before)','cw(7,o->c7_before)','R32(0x680818)=o->ve_before','R32(0x680810)=o->se_before','R32(0x68080c)=o->sy_before','R32(0x680814)=o->vs_before','R32(0x680808)=o->vc_before','R32(0x680804)=o->vt_before','R32(0x680800)=o->v_before','gate(4)']]
assert positions==sorted(positions)
assert not re.search(r'cw\((?:0x1b|0x22|0x33|0x06|6|0x16),',body)
assert read(C/'audit002.json')['passed'] and read(C/'closed001.json')['closed']
m=read(K/'model001.json');r=read(K/'integration005.json')
assert m['passed'] and r['passed'] and len(m['cases'])==614 and len(r['cases'])==604
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==490
 assert all(i in [0,1,2,3,4,5,7,0x10,0x1f,0x14,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert c['stack_bytes_written_from_top']<=6144 and c['admitted_stack_bytes']==6144
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='c10-'+phase+'-'+str(j))
  assert v[0]==(0x78933 if phase=='undo' else 0x78932)
  if phase=='undo':assert v[465]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='c10-coupling-'+str(j));assert v[0]==0x78933 and v[465]==1<<j and v[101]==0
for f in ['drop-write','wrong-write','drop-undo','wrong-undo']:
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='c10-'+f);assert v[0]==(0x78933 if f.endswith('undo') else 0x78932)
 if f.endswith('undo'):assert v[435]==8
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[460:466]==[212,233,1,233,212,0]
assert v[466:]==[n for x in [236,116,96,207,207,237,255,16] for n in [x,x,x]]
h=read(K/'host003.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload005.json')['unpadded_bytes']
assert rawsize==17240 and len(payload)==18432 and payload[rawsize:]==b'\xcc'*(18432-rawsize)
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x583c:0x5fe8]==bytes(0x7ac)
 assert b[0x5fe8:0x6000]==b'\xa5'*24 and b[0x6800:]==b'\xa5'*6144
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x6000)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x6000+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x1000-0x100000)
 assert b[0x1000:0x5800]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x6800,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x1000+18432==0x5800<0x583c<0x5840 and 0x5840+490*4==0x5fe8<0x6000 and 0x6000+256*8==0x6800<0x8000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x1000,0x5800],'request':[0x5800,0x583c],'request_guard':[0x583c,0x5840],'result':[0x5840,0x5fe8],'result_guard':[0x5fe8,0x6000],'IDT':[0x6000,0x6800],'stack':[0x6800,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
b=(P/'bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==new
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','vertical_display_end_cleanup_mask','vertical_total_cleanup_mask','vertical_crtc_cleanup_mask','CR07_cleanup_mask','CR10_cleanup_mask','CR10_before','CR10_after','CR10_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND','NVVVALIDEND']
schema={'passed':True,'rows':13,'columns':32,'offsets':new,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':22,'target_CR10':233,'limitations':'Same-value CR02/NVVVALIDSTART drops indistinguishable. Fourteen masks and neighbor/CPU/selector raw values omitted; final789 requires all22 clear. No native disk/fullmode/Windows proof.'}
stackmax=max(c['stack_bytes_written_from_top'] for c in r['cases'])
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True,'maximum_modeled_stack_bytes_written':stackmax,'stack_allocation_bytes':6144}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches788_except_namespace_native_CPU_guard':True,'frontend_matches787_except_namespace_report_offsets_and_reviewed_layout_changes':True,'result_bytes':1960,'result_end_offset':0x5fe8,'page_bounds':pages,'model_cases':614,'integration_cases':604,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit002.json'),'maximum_modeled_stack_bytes_written':stackmax})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS789 source, execution cases and independently checked memory layout')
