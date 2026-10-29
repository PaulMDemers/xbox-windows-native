"""Independent811 host-only source, bitmap, payload ownership and optical review.
Physical admission remains blocked until the separate cold810 control passes.
"""
from pathlib import Path
import re,json,hashlib,struct,datetime
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-high808';C=K.parent/'crtc-linecompare-bit809';P=Path('C:/xwn811/host007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
clean=lambda s:re.sub(r'\s+','',re.sub(r'/\*.*?\*/','',s,flags=re.S))
def ns(s,a):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+a+r'(?=[0-9a-f]{0,2}$)','0x811',p) if i%2 else p.replace(a,'811') for i,p in enumerate(parts))
body=ns((C/'probe.c').read_text(),'809')
guard='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)'
native='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)'
assert body.count(guard)==1;body=body.replace(guard,native);assert body==(K/'probe-native.c').read_text()
header=ns((C/'probe.h').read_text(),'809');assert header==(K/'probe.h').read_text()
for n in ['transaction.h','transaction811.c']:
 assert clean(ns((A/n.replace('811','808')).read_text(),'808'))==clean((K/n).read_text())
members=[]
for d in re.findall(r'uint32_t\s+([^;]+);',header):
 for part in d.split(','):
  m=re.fullmatch(r'\s*(\w+)(?:\[(\d+)\])?\s*',part);assert m
  members.extend([m[1]] if m[2] is None else [m[1]+'['+str(i)+']' for i in range(int(m[2]))])
assert len(members)==len(set(members))==790
cut=body.index(' for(unsigned i=0;i<7;++i)o->h_checked');head,tail=body[:cut],body[cut:]
assignments=re.findall(r'(?:o->\w+=)+0xffffffff;',head)
sentinels={n for statement in assignments for n in re.findall(r'o->(\w+)',statement)}
assert len(assignments)==348 and len(sentinels)==416
bitmap=(K/'probe-bitmap-native.c').read_text()
table=re.search(r'static const uint32_t sentinel_bits\[25\]=\{([^}]+)\};\n',bitmap);assert table
words=[int(n,16) for n in table[1].split(',')];assert len(words)==25
assert {members[i] for i in range(790) if words[i//32]>>(i%32)&1}==sentinels and words[-1]>>22==0
loop=' for(unsigned i=0;i<790;++i)if(sentinel_bits[i>>5]&(1u<<(i&31)))((uint32_t *)o)[i]=0xffffffff;\n'
assert bitmap.count(loop)==1
assert bitmap.replace(table[0],'').replace(loop,'').replace('__attribute__((noinline)) ','')==re.sub(r'(?:o->\w+=)+0xffffffff;','',head)+tail
assert read(K/'compaction-review001.json')['passed']
shown=[30,100,108,645,675,705,735,765];new=[0,0x8d4]+[0x6800+4*j for j in shown+[760,763,764]]
for n in ['main004.c','layout004.c','layout.h','plan.c','plan.h','page002.c','page.h','bridge003.S']:
 s=ns((A/n).read_text(),'808')
 if n!='layout004.c':s=s.replace('0x73e0','0x7458').replace('0xc20','0xc98');s=re.sub(r'\b3040\b','3160',s)
 if n=='main004.c':s=s.replace('payload_reloc,15,','payload_reloc,34,')
 if n=='page002.c':s=s.replace('count!=15','count!=34')
 if n=='bridge003.S':
  s=s.replace('0x8080000d','0x8110000d');a=s.index('report_offsets:\n');z=s.index('bridge_code_end:',a)
  s=s[:a]+'report_offsets:\n .long '+','.join(hex(x) for x in new)+'\n'+s[z:]
 assert clean(s)==clean((K/n).read_text()),n
assert 'memory.TotalPhysicalPages==16384' in (K/'main004.c').read_text()
assert 'frequency!=3375000' in (K/'main004.c').read_text()
assert not re.search(r'cw\((?:0x1b|0x22|0x33),',body)
positions=[body.index(t) for t in ['cw(9,o->cl9_target)','cw(9,o->cl9_before)','cw(7,o->cl7_before)','cw(0x15,o->cb15_before)','gate(4)']];assert positions==sorted(positions)
m=read(K/'model002.json');original=read(K/'model001.json');r=read(K/'integration012.json')
assert m['passed'] and original['passed'] and r['passed'] and len(m['cases'])==len(original['cases'])==1014 and len(r['cases'])==1004
assert read(K/'equivalence001.json')['exact_register_reads_writes_ports_and_790_dword_results']
assert m['ELF_sha256']==sha(Path('C:/xwn811/payload008/native.elf'))
for c in m['cases']:
 if c['name'].startswith('CPU-refused-') or c['name'] in ['PAE-refused','alternate-CR3','flags-0x202','flags-0x246']:
  assert c['raw_result'][0]!=0x811 and not c['writes'] and not c['ports'],c['name']
masks=[30,100,108,121,129,138,148,158,169,181,193,205,221,237,261,285,315,345,375,405,435,465,495,525,555,585,615,645,675,705,735,765]
for c in r['cases']:
 assert c['all_pixels_and_guards_exact'] and len(c['raw_result'])==790
 assert all(i in [0,1,2,3,4,5,6,7,9,0x10,0x12,0x1f,0x14,0x15,0x16,0x17,0x19,0x13] for i,x in c['CRTC_writes'])
 assert c['stack_bytes_written_from_top']<=384 and c['admitted_stack_bytes']==768
for phase in ['before','after','undo']:
 for j in range(9):
  v=next(c['raw_result'] for c in r['cases'] if c['name']=='cl9-'+phase+'-'+str(j));assert v[0]==(0x81147 if phase=='undo' else 0x81146)
  if phase=='undo':assert v[765]==1<<j and v[101]==0
for j in range(1,9):
 v=next(c['raw_result'] for c in r['cases'] if c['name']=='cl9-coupling-'+str(j));assert v[0]==0x81147 and v[765]==1<<j and v[101]==0
v=next(c['raw_result'] for c in r['cases'] if c['name']=='prefix-dual')
assert all(v[i]==0 for i in masks) and v[760:766]==[64,64,1,64,64,0]
assert v[766:]==[n for x in [12,62,233,223,223,140,255,16] for n in [x,x,x]]
for f in ['drop-write','wrong-write','drop-undo','wrong-undo','wrong-write-drop-undo']:
 v2=next(c['raw_result'] for c in r['cases'] if c['name']=='cl9-'+f);assert v2[0]==(0x811 if f in ['drop-write','drop-undo'] else 0x81146 if f=='wrong-write' else 0x81147)
 if f in ['wrong-undo','wrong-write-drop-undo']:assert v2[765]==1 and v2[101]==0
h=read(K/'host007.json');pages=[];payload=(P/'payload.bin').read_bytes();rawsize=read(K/'payload008.json')['unpadded_bytes']
assert rawsize==23212 and len(payload)==24256 and payload[rawsize:]==b'\xcc'*1044
assert h['bridge_symbols']['bridge_code_end']<=0x800 and len((P/'bridge.bin').read_bytes())==0x900
for layout in ['dual','identity','relocated','scatter']:
 b=(P/layout/'page.bin').read_bytes();base=struct.unpack_from('<I',b,0x844)[0]
 assert len(b)==32768 and b[0x67fc:0x7458]==bytes(0xc5c)
 assert b[0x7458:0x7500]==b'\xa5'*168 and b[0x7d00:]==b'\xa5'*768
 assert struct.unpack_from('<HI',b,0x830)==(2047,base+0x7500)
 target=base+h['bridge_symbols']['bridge_fault']
 for i in range(256):assert struct.unpack_from('<4H',b,0x7500+8*i)==(target&65535,0x10,0x8e00,target>>16)
 expected=bytearray(payload)
 for x in h['relocations']:
  if x['type']=='R_386_32':struct.pack_into('<I',expected,x['offset'],x['value']+base+0x900-0x100000)
 assert b[0x900:0x67c0]==expected
 checksum=sum(struct.unpack_from('<I',b,i)[0] for i in range(0,0x7d00,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 assert struct.unpack_from('<I',b,0x854)[0]==checksum
 assert 0x900+24256==0x67c0<0x67fc<0x6800 and 0x6800+790*4==0x7458<0x7500 and 0x7500+256*8==0x7d00<0x8000
 pages.append({'layout':layout,'sha256':sha(P/layout/'page.bin'),'payload':[0x900,0x67c0],'request':[0x67c0,0x67fc],'result':[0x6800,0x7458],'IDT':[0x7500,0x7d00],'stack':[0x7d00,0x8000],'all256IDTentries_exact':True,'relocated_payload_and_checksum_exact':True})
b=(P/'bridge.bin').read_bytes();assert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==new
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR09_blank_cleanup_mask','CR07_blank_cleanup_mask','CR15_blank_cleanup_mask','CR07_linecompare_cleanup_mask','CR09_linecompare_cleanup_mask','CR09_linecompare_before','CR09_linecompare_after','CR09_linecompare_restored']
omitted=[i for i in masks if i not in shown];assert len(omitted)==24
schema={'passed':True,'rows':13,'columns':32,'offsets':new,'names':names,'bit_order':'MSB left white1 black0 gray background','omitted_aggregate_masks':omitted,'total_masks_required_for_success':32,'target_CR09_linecompare':64,'limitations':'Same-value CR09 write/undo drops indistinguishable.24 masks and neighbors aggregate-only. No fullmode or Windows proof.'}
stackmax=max(c['stack_bytes_written_from_top'] for c in r['cases'])
for n,obj in [('optical-schema001.json',schema),('layout-independent001.json',{'passed':True,'physical_access':False,'checks':pages,'payload_IDT_result_stack_disjoint':True,'maximum_modeled_stack_bytes_written':stackmax,'stack_allocation_bytes':768}),('source-review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_access':False,'hardware_admission':False,'waiting_for':'cold810 physical PASS','probe_matches809_except_namespace_native_CPU_guard':True,'all790_bitmap_bits_match416_sentinels':True,'pure_result_compaction_reviewed':True,'result_bytes':3160,'model_cases':1014,'integration_cases':1004,'failed_recovery_inhibits_output':True,'maximum_modeled_stack_bytes_written':stackmax})]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS811 host-only source, execution, memory and optical checks; hardware remains blocked')
