"""Independent804 source, ELF execution, full-page bounds and optical schema review."""
from pathlib import Path
import re,json,datetime,hashlib,struct
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-bit801';C=K.parent/'crtc-vblank-overflow803';P=Path('C:/xwn804/host007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
def ns(s,a,b):
 # Status/tag namespace only; leave full-length hardware and CPU constants intact.
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+a+r'(?=[0-9a-f]{0,2}$)','0x'+b,p) if i%2 else p.replace(a,b) for i,p in enumerate(parts))
body=ns((C/'probe.c').read_text(),'803','804')
guard='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)'
native='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)'
assert body.count(guard)==1;body=body.replace(guard,native)
assert clean(body)==clean((K/'probe-native.c').read_text())
assert clean(ns((C/'probe.h').read_text(),'803','804'))==clean((K/'probe.h').read_text())
for n in ['transaction.h','transaction804.c']:
 assert clean(ns((A/n.replace('804','801')).read_text(),'801','804'))==clean((K/n).read_text())
# Reconstruct compact sentinel initialization independently of its generator.
cut=body.index(' for(unsigned i=0;i<7;++i)o->h_checked');head,tail=body[:cut],body[cut:];fields=[]
def remove(m):fields.extend(reversed(re.findall(r'o->(\w+)',m[1])));return ''
head,groups=re.subn(r'((?:o->\w+=)+)0xffffffff;',remove,head)
assert groups==294 and len(fields)==len(set(fields))==362
table='static const uint16_t sentinel_offsets[] = {\n'+''.join(' (uint16_t)__builtin_offsetof(struct result804,'+f+'),\n' for f in fields)+'};\n'
head=head.replace('void probe804(',table+'void probe804(')
loop=' for(unsigned i=0;i<sizeof(sentinel_offsets)/sizeof(sentinel_offsets[0]);++i)\n  *(uint32_t *)((uint8_t *)o+sentinel_offsets[i])=0xffffffff;\n'
compact=head+loop+tail
assert clean(compact)==clean((K/'probe-compact-native.c').read_text())
shared=compact.replace('static uint8_t cr(','static __attribute__((noinline)) uint8_t cr(').replace('static void cw(','static __attribute__((noinline)) void cw(')
assert clean(shared)==clean((K/'probe-shared-native.c').read_text())
assert shared.count('__attribute__((noinline))')==2
# Exact source-only frontend delta, independent numeric token substitution.
mapping={'23040':'22656','0x5a00':'0x5880','0x6a00':'0x6880','0x6a04':'0x6884','0x6a3c':'0x68bc','0x6a40':'0x68c0','0x74b8':'0x73b0','0xab8':'0xb30'}
old=[0,0x8d4]+[0x6a40+4*j for j in [30,100,108,525,555,585,615,645,640,643,644]]
new=[0,0x8d4]+[0x68c0+4*j for j in [30,100,108,555,585,615,645,675,670,673,674]]
for n in ['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','bridge003.S']:
 s=ns((A/n).read_text(),'801','804')
 if n=='bridge003.S':s=s.replace(','.join(hex(i) for i in old[1:]),'OFFSETS').replace('0x8010000d','0x8040000d')
 if n!='layout004.c':s=re.sub(r'(?<![0-9a-zA-Z])(?:'+'|'.join(map(re.escape,mapping))+r')(?![0-9a-zA-Z])',lambda m:mapping[m[0]],s)
 s=s.replace('OFFSETS',','.join(hex(i) for i in new[1:]))
 if n=='bridge003.S':s=s.replace('.long 0,0x8d4','.long 0x0,0x8d4')
 if n=='main004.c':s=s.replace('payload_reloc,14,','payload_reloc,15,')
 if n=='page002.c':s=s.replace('count!=14','count!=15')
 assert clean(s)==clean((K/n).read_text()),n
assert 'memory.TotalPhysicalPages==16384' in (K/'main004.c').read_text()
assert 'frequency!=3375000' in (K/'main004.c').read_text()
assert '{0xb0000,0x5a00}' in (K/'layout004.c').read_text()
assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
positions=[body.index(t) for t in ['cw(9,o->cb9_target)','cw(7,o->cb7_target)','cw(7,o->cb7_before)','cw(9,o->cb9_before)','cw(0x12,o->cd12_before)','gate(4)']]
assert positions==sorted(positions)
assert read(C/'audit002.json')['passed'] and read(C/'closed001.json')['closed']
assert read(A/'audit001.json')['passed'] and read(A/'closed001.json')['closed']
m=read(K/'model002.json');original=read(K/'model001.json');r=read(K/'integration010.json')
assert m['passed'] and original['passed'] and r['passed'] and len(m['cases'])==len(original['cases'])==894 and len(r['cases'])==884
assert read(K/'equivalence001.json')['exact_register_reads_writes_ports_and_700_dword_results']
assert m['ELF_sha256']==sha(Path('C:/xwn804/payload008/native.elf'))
for c in m['cases']:
 if c['name'].startswith('CPU-refused-') or c['name'] in ['PAE-refused','alternate-CR3','flags-0x202','flags-0x246']:
  assert c['raw_result'][0]!=0x804 and not c['writes'] and not c['ports'],c['name']
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615,645,675]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==700
 assert all(i in [0,1,2,3,4,5,6,7,9,0x10,0x12,0x1f,0x14,0x16,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert c['stack_bytes_written_from_top']<=384 and c['admitted_stack_bytes']==768
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='cb7-'+phase+'-'+str(j))
  assert v[0]==(0x80441 if phase=='undo' else 0x80440)
  if phase=='undo':assert v[675]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='cb7-coupling-'+str(j));assert v[0]==0x80441 and v[675]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[670:676]==[54,62,1,62,54,0]
assert v[676:]==[n for x in [12,64,233,223,207,140,255,16] for n in [x,x,x]]
for f in ['drop-write','wrong-write','drop-undo','wrong-undo','wrong-write-drop-undo']:
 v2=next(c['raw_result'] for c in r['cases'] if c['name']=='cb7-'+f)
 assert v2[0]==(0x80440 if f in ['drop-write','wrong-write'] else 0x80441)
 if f in ['drop-undo','wrong-undo','wrong-write-drop-undo']:assert v2[675]==1 and v2[101]==0
h=read(K/'host007.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload008.json')['unpadded_bytes']
assert rawsize==22592 and len(payload)==22656 and payload[rawsize:]==b'\xcc'*64
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x68bc:0x73b0]==bytes(0xaf4)
 assert b[0x73b0:0x7500]==b'\xa5'*336 and b[0x7d00:]==b'\xa5'*768
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x7500)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x7500+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x1000-0x100000)
 assert b[0x1000:0x6880]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x7d00,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x1000+22656==0x6880<0x68bc<0x68c0 and 0x68c0+700*4==0x73b0<0x7500 and 0x7500+256*8==0x7d00<0x8000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x1000,0x6880],'request':[0x6880,0x68bc],'request_guard':[0x68bc,0x68c0],'result':[0x68c0,0x73b0],'result_guard':[0x73b0,0x7500],'IDT':[0x7500,0x7d00],'stack':[0x7d00,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
b=(P/'bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==new
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR16_blank_end_cleanup_mask','CR07_display_cleanup_mask','CR12_display_cleanup_mask','CR09_blank_cleanup_mask','CR07_blank_cleanup_mask','CR07_blank_before','CR07_blank_after','CR07_blank_restored']
shown=[30,100,108,555,585,615,645,675];omitted=[i for i in masks if i not in shown];assert len(omitted)==21
schema={'passed':True,'rows':13,'columns':32,'offsets':new,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':29,'target_CR07_blank':62,'limitations':'Same-value CR02/NVVVALIDSTART/CR07total drops indistinguishable. Twenty-one masks and neighbor/CPU/selector values omitted; final804 requires all29 clear. No native disk/fullmode/Windows proof.'}
stackmax=max(c['stack_bytes_written_from_top'] for c in r['cases'])
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True,'maximum_modeled_stack_bytes_written':stackmax,'stack_allocation_bytes':768}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'probe_matches803_except_scoped_namespace_native_CPU_guard':True,'compact_initialization_exact_fields_and_hardware_tail':True,'shared_helpers_only_noinline':True,'frontend_matches801_except_namespace_report_offsets_layout_and_relocation_count':True,'result_bytes':2800,'result_end_offset':0x73b0,'page_bounds':pages,'model_cases':894,'integration_cases':884,'failed_recovery_inhibits_output':True,'kernel_audit_sha256':sha(C/'audit002.json'),'maximum_modeled_stack_bytes_written':stackmax})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS804 independent source, execution, memory-layout and optical schema review')
