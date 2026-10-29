"""Independent source reconstruction, result layout and optical schema review."""
from pathlib import Path
import re,json,hashlib,datetime
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-bit811';B=K.parent/'crtc-linecompare-low812'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x813',p).replace('0x'+old+'0000d','0x8130000d') if i%2 else p.replace(old,'813') for i,p in enumerate(parts))
body=ns((B/'probe.c').read_text(),'812')
old='(o->cr0&0x80000001)!=0x80000001 || (o->cr4&0x20)'
new='(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200) || (o->cr4&0x20)'
assert body.count(old)==1;body=body.replace(old,new)
assert body==(K/'probe-native.c').read_text()
header=ns((B/'probe.h').read_text(),'812');assert header==(K/'probe.h').read_text()
members=[]
for d in re.findall(r'uint32_t\s+([^;]+);',header):
 for part in d.split(','):
  m=re.fullmatch(r'\s*(\w+)(?:\[(\d+)\])?\s*',part);assert m
  members.extend([m[1]] if m[2] is None else [m[1]+'['+str(i)+']' for i in range(int(m[2]))])
assert len(members)==len(set(members))==820
cut=body.index(' for(unsigned i=0;i<7;++i)o->h_checked');head,tail=body[:cut],body[cut:]
sentinels={n for statement in re.findall(r'(?:o->\w+=)+0xffffffff;',head) for n in re.findall(r'o->(\w+)',statement)}
bitmap=(K/'probe-bitmap-native.c').read_text()
table=re.search(r'static const uint32_t sentinel_bits\[26\]=\{([^}]+)\};\n',bitmap);assert table
bits=[int(n,16) for n in table[1].split(',')]
assert {members[i] for i in range(820) if bits[i//32]>>(i%32)&1}==sentinels and bits[-1]>>20==0
loop=' for(unsigned i=0;i<820;++i)if(sentinel_bits[i>>5]&(1u<<(i&31)))((uint32_t *)o)[i]=0xffffffff;\n'
assert bitmap.count(loop)==1
assert bitmap.replace(table[0],'').replace(loop,'').replace('__attribute__((noinline)) ','')==re.sub(r'(?:o->\w+=)+0xffffffff;','',head)+tail
s=(K/'probe-pairs-native.c').read_text();a=s.index('struct recovery_pair {');z=s.index('void probe813(',a)
helper=s[a:z];tables=re.findall(r'static const struct recovery_pair (pairs_\w+)\[\]=\{(.*?)\};',helper)
assert len(tables)==20
for name,table in tables:
 pairs=re.findall(r'\{__builtin_offsetof\(struct result813,(\w+)\),__builtin_offsetof\(struct result813,(\w+)\)\}',table)
 assert len(pairs) in (7,9)
 assert table==','.join('{__builtin_offsetof(struct result813,'+x+'),__builtin_offsetof(struct result813,'+y+')}' for x,y in pairs)
 mask=name.removeprefix('pairs_');call='o->'+mask+'|=compare_pairs(o,'+name+','+str(len(pairs))+');';assert s.count(call)==1
 candidates=re.findall(r'(?:if\(o->\w+!=o->\w+\)o->'+mask+r'\|=(?:0x[0-9a-f]+|[0-9]+);)+',bitmap);assert len(candidates)==1
 wanted=''.join('if(o->'+x+'!=o->'+y+')o->'+mask+'|='+str(1<<i)+';' for i,(x,y) in enumerate(pairs))
 assert re.sub(r'\|=(0x[0-9a-f]+|[0-9]+);',lambda m:'|='+str(int(m[1],0))+';',candidates[0])==wanted
 s=s.replace(call,candidates[0])
s=s[:s.index('struct recovery_pair {')]+s[s.index('void probe813(',s.index('struct recovery_pair {')):]
assert s==bitmap
parent=(A/'probe-pairs-native.c').read_text();pa=parent.index('struct recovery_pair {');pz=parent.index('static const struct recovery_pair ',pa)
assert helper[:helper.index('static const struct recovery_pair ')]==ns(parent[pa:pz],'811')
for n in ['transaction.h','transaction813.c']:
 assert (K/n).read_text()==ns((A/n.replace('813','811')).read_text(),'811')
assert not re.search(r'cw\((?:0x1a|0x1b|0x22|0x25|0x28|0x2d|0x33),',body)
positions=[body.index(t) for t in ['cw(0x18,o->cl18_target)','cw(0x18,o->cl18_before)','cw(9,o->cl9_before)','gate(4)']];assert positions==sorted(positions)
masks=[i for i,n in enumerate(members) if n.endswith('cleanup_mask')]
assert 795 in masks
shown=[30,100,108,675,705,735,765,795];rows=[0,0x8d4]+[0x6800+4*j for j in shown+[790,793,794]]
bridge=(K/'bridge003.S').read_text();report=bridge.split('report_offsets:\n .long ')[1].split('\n')[0]
assert [int(x,16) for x in report.split(',')]==rows
assert 0x6800+820*4==0x74d0<0x7500 and 0x7d00+768==0x8000
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_only_parents':True,'kernel812_to_native_only_CPU_guard_delta':True,'reverse_compaction_exact':True,'pure_comparison_groups':20,'sentinel_fields':len(sentinels),'result_words':820,'all_mask_indices':masks,'displayed_masks':shown,'omitted_aggregate_masks':[i for i in masks if i not in shown],'report_word_indices':[0,1]+shown+[790,793,794],'physical_access':False,'limits':['Same-value CR18 effectiveness unproved','No new full-mode/Windows proof']}
with (K/'source-review001.json').open('x') as f:json.dump(r,f,indent=2)
print('PASS independent native813 source, compaction and 820-word optical layout')
