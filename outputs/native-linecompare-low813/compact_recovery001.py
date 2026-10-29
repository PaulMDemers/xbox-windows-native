"""Compact pure result-field comparisons; preserve all device accesses and order."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;s=(K/'probe-bitmap-native.c').read_text();tables=[];groups=[]
pattern=r'(?:if\(o->\w+!=o->\w+\)o->\w+\|=(?:0x[0-9a-f]+|[0-9]+);)+'
def replace(m):
 terms=re.findall(r'if\(o->(\w+)!=o->(\w+)\)o->(\w+)\|=(0x[0-9a-f]+|[0-9]+);',m[0])
 if len(terms)<4:return m[0]
 mask=terms[0][2];assert all(t[2]==mask and int(t[3],0)==1<<i for i,t in enumerate(terms))
 name='pairs_'+mask
 table='static const struct recovery_pair '+name+'[]={'+','.join('{__builtin_offsetof(struct result813,'+a+'),__builtin_offsetof(struct result813,'+b+')}' for a,b,_,_ in terms)+'};\n'
 tables.append(table);groups.append(dict(mask=mask,pairs=[[a,b] for a,b,_,_ in terms],original=m[0],replacement='o->'+mask+'|=compare_pairs(o,'+name+','+str(len(terms))+');'))
 return groups[-1]['replacement']
out=re.sub(pattern,replace,s);assert len(groups)==20
helper='''struct recovery_pair {uint16_t left,right;};
static __attribute__((noinline)) uint32_t compare_pairs(const struct result813 *o,const struct recovery_pair *p,unsigned count)
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
at=out.index('void probe813(');out=out[:at]+helper+''.join(tables)+out[at:]
with (K/'probe-pairs-native.c').open('xb') as f:f.write(out.encode())
(K/'recovery-compaction001.json').write_text(json.dumps(dict(source_only=True,qualification=False,physical_access=False,groups=groups,input_sha256=hashlib.sha256(s.encode()).hexdigest(),output_sha256=hashlib.sha256(out.encode()).hexdigest()),indent=2)+'\n')
m=(K/'measure002.py').read_text().replace('measure002','measure003').replace("'probe-bitmap-native.c'","'probe-pairs-native.c'").replace('bitmap-native','pairs-native')
with (K/'measure003.py').open('xb') as f:f.write(m.encode())
print('19 result-only comparison groups compacted; equivalence pending')
