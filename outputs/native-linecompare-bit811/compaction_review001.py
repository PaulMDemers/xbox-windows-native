"""Reverse each result-only replacement independently; check table offsets/layout."""
from pathlib import Path
import re,json,hashlib,datetime,struct
K=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest()
original=(K/'probe-bitmap-native.c').read_bytes();data=(K/'probe-pairs-native.c').read_bytes();s=data.decode()
start=s.index('struct recovery_pair {');end=s.index('void probe811(',start)
helper=s[start:end];tables=re.findall(r'static const struct recovery_pair (pairs_\w+)\[\]=\{(.*?)\};',helper)
assert len(tables)==19
for name,table in tables:
 pairs=re.findall(r'\{__builtin_offsetof\(struct result811,(\w+)\),__builtin_offsetof\(struct result811,(\w+)\)\}',table)
 assert len(pairs) in (7,9)
 assert table==','.join('{__builtin_offsetof(struct result811,'+a+'),__builtin_offsetof(struct result811,'+b+')}' for a,b in pairs)
 mask=name.removeprefix('pairs_');call='o->'+mask+'|=compare_pairs(o,'+name+','+str(len(pairs))+');'
 assert s.count(call)==1
 # Numeric constants may differ in spelling; reconstruct from original statements.
 wanted=''.join('if(o->'+a+'!=o->'+b+')o->'+mask+'|='+str(1<<i)+';' for i,(a,b) in enumerate(pairs))
 candidates=re.findall(r'(?:if\(o->\w+!=o->\w+\)o->'+mask+r'\|=(?:0x[0-9a-f]+|[0-9]+);)+',original.decode())
 assert len(candidates)==1
 canonical=re.sub(r'\|=(0x[0-9a-f]+|[0-9]+);',lambda m:'|='+str(int(m[1],0))+';',candidates[0]);assert canonical==wanted
 s=s.replace(call,candidates[0])
s=s[:s.index('struct recovery_pair {')]+s[s.index('void probe811(',s.index('struct recovery_pair {')):]
assert s.encode()==original
expected='''struct recovery_pair {uint16_t left,right;};
static __attribute__((noinline)) uint32_t compare_pairs(const struct result811 *o,const struct recovery_pair *p,unsigned count)
{
 uint32_t mask=0;
 for(unsigned i=0;i<count;++i){
  uint32_t a=*(const uint32_t *)((const uint8_t *)o+p[i].left);
  uint32_t b=*(const uint32_t *)((const uint8_t *)o+p[i].right);
  if(a!=b)mask|=1u<<i;
 }
 return mask;
}
'''
assert helper[:helper.index('static const struct recovery_pair')]==expected
eq=json.loads((K/'equivalence001.json').read_text());assert eq['passed'] and eq['case_count']==1014
r={'passed':True,'physical_access':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':19,'reverse_transform_exact':True,'result_only_helper_exact':True,'device_operations_unchanged':True,'execution_equivalence_cases':1014,'pins':{n:sha((K/n).read_bytes()) for n in ['probe-bitmap-native.c','probe-pairs-native.c','equivalence001.json']},'limits':'Host model only; added normal-memory instructions do not establish hardware timing equivalence.'}
(K/'compaction-review001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS exact reverse transformation of19 pure result comparison groups')
