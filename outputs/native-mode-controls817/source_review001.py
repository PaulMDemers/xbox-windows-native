"""Independent reverse-compaction and explicit40KiB layout review."""
from pathlib import Path
import re,json,hashlib,datetime
K=Path(__file__).resolve().parent;B=K.parent/'crtc-mode-controls816'
def ns(s):
 p=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x816(?=[0-9a-f]{0,2}$)','0x817',v) if i%2 else v.replace('816','817') for i,v in enumerate(p))
body=ns((B/'probe.c').read_text());old='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)';new='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)'
assert body.count(old)==1;body=body.replace(old,new);assert body==(K/'probe-native.c').read_text()
header=ns((B/'probe.h').read_text());assert header==(K/'probe.h').read_text()
members=[]
for d in re.findall(r'uint32_t\s+([^;]+);',header):
 for part in d.split(','):
  m=re.fullmatch(r'\s*(\w+)(?:\[(\d+)\])?\s*',part);assert m
  members.extend([m[1]] if m[2] is None else [m[1]+'['+str(i)+']' for i in range(int(m[2]))])
assert len(members)==len(set(members))==917
cut=body.index(' for(unsigned i=0;i<7;++i)o->h_checked');head,tail=body[:cut],body[cut:]
sentinels={n for statement in re.findall(r'(?:o->\w+=)+0xffffffff;',head) for n in re.findall(r'o->(\w+)',statement)}
bitmap=(K/'probe-bitmap-native.c').read_text();table=re.search(r'static const uint32_t sentinel_bits\[29\]=\{([^}]+)\};\n',bitmap);assert table
bits=[int(n,16) for n in table[1].split(',')]
assert {members[i] for i in range(917) if bits[i//32]>>(i%32)&1}==sentinels and bits[-1]>>21==0
loop=' for(unsigned i=0;i<917;++i)if(sentinel_bits[i>>5]&(1u<<(i&31)))((uint32_t *)o)[i]=0xffffffff;\n'
assert bitmap.count(loop)==1
unbitmap=bitmap.replace(table[0],'').replace(loop,'').replace('static __attribute__((noinline)) uint8_t cr(','static uint8_t cr(').replace('static __attribute__((noinline)) void cw(','static void cw(')
assert unbitmap==re.sub(r'(?:o->\w+=)+0xffffffff;','',head)+tail
s=(K/'probe-pairs-native.c').read_text();a=s.index('struct recovery_pair {');z=s.index('void probe817(',a);helper=s[a:z]
tables=re.findall(r'static const struct recovery_pair (pairs_\w+)\[\]=\{(.*?)\};',helper);assert len(tables)==20
for name,table in tables:
 pairs=re.findall(r'\{__builtin_offsetof\(struct result817,(\w+)\),__builtin_offsetof\(struct result817,(\w+)\)\}',table);assert len(pairs) in (7,9)
 mask=name.removeprefix('pairs_');call='o->'+mask+'|=compare_pairs(o,'+name+','+str(len(pairs))+');';assert s.count(call)==1
 candidates=re.findall(r'(?:if\(o->\w+!=o->\w+\)o->'+mask+r'\|=(?:0x[0-9a-f]+|[0-9]+);)+',bitmap);assert len(candidates)==1
 wanted=''.join('if(o->'+x+'!=o->'+y+')o->'+mask+'|='+str(1<<i)+';' for i,(x,y) in enumerate(pairs))
 assert re.sub(r'\|=(0x[0-9a-f]+|[0-9]+);',lambda m:'|='+str(int(m[1],0))+';',candidates[0])==wanted
 s=s.replace(call,candidates[0])
s=s[:s.index('struct recovery_pair {')]+s[s.index('void probe817(',s.index('struct recovery_pair {')):];assert s==bitmap
masks=[i for i,n in enumerate(members) if n.endswith('cleanup_mask')];assert len(masks)==34
shown=[30,100,108,675,735,795,915];rows=[0,0x8d4]+[0x7800+4*j for j in shown+[916,820,835,905]]
assert members[915:917]==['mc_cleanup_mask','mc_forward_mask']
assert members[820]=='mc_before[0]' and members[835]=='mc_after[0]' and members[905]=='mc_undo[30]'
# The final undo value for CR1A is in the LAST executed undo step, index0.
# mc_undo[30] is the first undo step and still contains the changed CR1A.
assert rows[-1]==0x8624
bridge=(K/'bridge003.S').read_text();report=bridge.split('report_offsets:\n .long ')[1].split('\n')[0]
assert [int(x,16) for x in report.split(',')]==rows
assert 2304+28352==0x77c0 and 0x77c0+60<=0x7800 and 0x7800+917*4==0x8654<0x8700
assert 0x8700+2048==0x8f00 and 0x8f00+4352==40960
page=(K/'page002.c').read_text();assert 'w32(p,0x808,0xffff)' in page
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,kernel816_only_CPU_guard_delta=True,reverse_compaction_exact=True,result_words=917,all_mask_indices=masks,displayed_cleanup_masks=shown,displayed_forward_mask=916,omitted_aggregate_masks=[i for i in masks if i not in shown],report_word_indices=[0,1]+shown+[916,820,835,905],allocation_bytes=40960,stack_bytes=4352,optical_last_value='CR1A after undo of CR2D, before own undo; not final CR1A restoration')
with (K/'source-review001.json').open('x') as f:json.dump(r,f,indent=2)
print('PASS reverse source/compaction and40KiB layout; report last value is interim CR1A')
