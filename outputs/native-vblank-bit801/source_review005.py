"""Independent801 source derivation, result contract, bounds and report review."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;O=K.parent/'native-vdisplay-low799';C=K.parent/'crtc-vblank-bit800';P=Path('C:/xwn801/host007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
def ns(s,a,b):
 # Only short status constants are renumbered; CPU masks are NEVER identifiers.
 return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]{0,2}\b)','0x'+b,s))
body=ns((C/'probe.c').read_text(),'800','801')
guard='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)'
native='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)'
assert body.count(guard)==1;body=body.replace(guard,native)
assert clean(body)==clean((K/'probe-native.c').read_text())
assert clean(ns((C/'probe.h').read_text(),'800','801'))==clean((K/'probe.h').read_text())
for n in ['transaction.h','transaction801.c']:
 assert clean(ns((O/n.replace('801','799')).read_text(),'799','801'))==clean((K/n).read_text())
# Independently reconstruct compact initializer, including exact field order.
cut=body.index(' for(unsigned i=0;i<7;++i)o->h_checked');head,tail=body[:cut],body[cut:];fields=[]
def remove(m):fields.extend(reversed(re.findall(r'o->(\w+)',m[1])));return ''
head,groups=re.subn(r'((?:o->\w+=)+)0xffffffff;',remove,head)
assert groups==276 and len(fields)==len(set(fields))==344
table='static const uint16_t sentinel_offsets[] = {\n'+''.join(' (uint16_t)__builtin_offsetof(struct result801,'+f+'),\n' for f in fields)+'};\n'
head=head.replace('void probe801(',table+'void probe801(')
loop=' for(unsigned i=0;i<sizeof(sentinel_offsets)/sizeof(sentinel_offsets[0]);++i)\n  *(uint32_t *)((uint8_t *)o+sentinel_offsets[i])=0xffffffff;\n'
assert clean(head+loop+tail)==clean((K/'probe-compact-native.c').read_text())
# Check frontend source delta without a generic 512 replacement (pixel origin).
mapping={'23424':'23040','0x5b80':'0x5a00','0x6b80':'0x6a00','0x6b84':'0x6a04','0x6bbc':'0x6a3c','0x6bc0':'0x6a40','0x75c0':'0x74b8','0x7600':'0x7500','0x7e00':'0x7d00','0xa40':'0xab8'}
old=[0,0x8d4]+[0x6bc0+4*j for j in [30,100,108,495,525,555,585,615,610,613,614]]
new=[0,0x8d4]+[0x6a40+4*j for j in [30,100,108,525,555,585,615,645,640,643,644]]
for n in ['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','bridge003.S']:
 s=ns((O/n.replace('bridge003','bridge002')).read_text(),'799','801')
 if n=='bridge003.S':s=s.replace(','.join(hex(i) for i in old[1:]),'OFFSET_PLACEHOLDER').replace('0x7990000d','0x8010000d')
 s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
 s=s.replace('OFFSET_PLACEHOLDER',','.join(hex(i) for i in new[1:]))
 if n=='main004.c':s=s.replace('payload_reloc,13,','payload_reloc,14,')
 if n=='page002.c':s=s.replace('count!=13','count!=14')
 assert clean(s)==clean((K/n).read_text()),n
assert 'memory.TotalPhysicalPages==16384' in (K/'main004.c').read_text()
assert 'frequency!=3375000' in (K/'main004.c').read_text()
assert '{0xb0000,0x5a00}' in (K/'layout004.c').read_text()
assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
positions=[body.index(t) for t in ['cw(0x12,o->cd12_target)','cw(9,o->cb9_target)','cw(9,o->cb9_before)','cw(0x12,o->cd12_before)','cw(7,o->cd7_before)','gate(4)']]
assert positions==sorted(positions)
assert read(C/'audit001.json')['passed'] and read(C/'closed001.json')['closed']
assert read(O/'audit001.json')['passed'] and read(O/'closed001.json')['closed']
m=read(K/'model004.json');original=read(K/'model003.json');r=read(K/'integration010.json')
assert m['passed'] and original['passed'] and r['passed'] and len(m['cases'])==len(original['cases'])==854 and len(r['cases'])==844
assert read(K/'equivalence002.json')['exact_register_reads_writes_ports_and_670_dword_results']
assert m['ELF_sha256']==sha(Path('C:/xwn801/payload008/native.elf'))
for c in m['cases']:
 if c['name'].startswith('CPU-refused-') or c['name'] in ['PAE-refused','alternate-CR3','flags-0x202','flags-0x246']:
  assert c['raw_result'][0]!=0x801 and not c['writes'] and not c['ports'],c['name']
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615,645]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==670
 assert all(i in [0,1,2,3,4,5,6,7,9,0x10,0x12,0x1f,0x14,0x16,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert c['stack_bytes_written_from_top']<=384 and c['admitted_stack_bytes']==768
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='cb9-'+phase+'-'+str(j))
  assert v[0]==(0x8013f if phase=='undo' else 0x8013e)
  if phase=='undo':assert v[645]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='cb9-coupling-'+str(j));assert v[0]==0x8013f and v[645]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[640:646]==[96,64,1,64,96,0]
assert v[646:]==[n for x in [12,54,233,223,207,140,255,16] for n in [x,x,x]]
for f in ['drop-write','wrong-write','drop-undo','wrong-undo','wrong-write-drop-undo']:
 v2=next(c['raw_result'] for c in r['cases'] if c['name']=='cb9-'+f)
 assert v2[0]==(0x8013e if f in ['drop-write','wrong-write'] else 0x8013f)
 if f in ['drop-undo','wrong-undo','wrong-write-drop-undo']:assert v2[645]==1 and v2[101]==0
h=read(K/'host007.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload008.json')['unpadded_bytes']
assert rawsize==22968 and len(payload)==23040 and payload[rawsize:]==b'\xcc'*72
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x6a3c:0x74b8]==bytes(0xa7c)
 assert b[0x74b8:0x7500]==b'\xa5'*72 and b[0x7d00:]==b'\xa5'*768
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x7500)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x7500+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x1000-0x100000)
 assert b[0x1000:0x6a00]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x7d00,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x1000+23040==0x6a00<0x6a3c<0x6a40 and 0x6a40+670*4==0x74b8<0x7500 and 0x7500+256*8==0x7d00<0x8000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x1000,0x6a00],'request':[0x6a00,0x6a3c],'request_guard':[0x6a3c,0x6a40],'result':[0x6a40,0x74b8],'result_guard':[0x74b8,0x7500],'IDT':[0x7500,0x7d00],'stack':[0x7d00,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
b=(P/'bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==new
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR06_total_cleanup_mask','CR16_blank_end_cleanup_mask','CR07_display_cleanup_mask','CR12_display_cleanup_mask','CR09_blank_cleanup_mask','CR09_blank_before','CR09_blank_after','CR09_blank_restored']
omitted=['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVDISPEND','NVVTOTAL','NVVCRTC','NVVVALIDSTART','NVVSYNCSTART','NVVSYNCEND','NVVVALIDEND','CR07sync','CR10','CR07total']
schema={'passed':True,'rows':13,'columns':32,'offsets':new,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':28,'target_CR09_blank':64,'limitations':'Same-value CR02/NVVVALIDSTART/CR07total drops indistinguishable. Twenty masks and neighbor/CPU/selector values omitted; final801 requires all28 clear. No native disk/fullmode/Windows proof.'}
stackmax=max(c['stack_bytes_written_from_top'] for c in r['cases'])
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True,'maximum_modeled_stack_bytes_written':stackmax,'stack_allocation_bytes':768}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches800_except_scoped_namespace_native_CPU_guard':True,'compact_initialization_exact_fields_and_hardware_tail':True,'frontend_matches799_except_namespace_report_offsets_layout_and_relocation_count':True,'result_bytes':2680,'result_end_offset':0x74b8,'page_bounds':pages,'model_cases':854,'integration_cases':844,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit001.json'),'maximum_modeled_stack_bytes_written':stackmax})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS801 independent source, execution, memory-layout and optical schema review')
