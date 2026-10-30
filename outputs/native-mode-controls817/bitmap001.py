"""Compact sentinel initialization as a bitmap, preserving hardware operation tail."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent
s=(K/'probe-native.c').read_text();cut=s.index(' for(unsigned i=0;i<7;++i)o->h_checked');head,tail=s[:cut],s[cut:];fields=[]
def remove(m):fields.extend(reversed(re.findall(r'o->(\w+)',m[1])));return ''
head,groups=re.subn(r'((?:o->\w+=)+)0xffffffff;',remove,head)
h=(K/'probe.h').read_text();body=h[h.index('{')+1:h.index('};')];names=[]
for declaration in body.split(';'):
 declaration=declaration.strip()
 if not declaration:continue
 assert declaration.startswith('uint32_t '),declaration
 for name in declaration[len('uint32_t '):].split(','):
  name=name.strip();m=re.fullmatch(r'(\w+)\[(\d+)\]',name)
  if m:names.extend([m[1]+'['+str(i)+']' for i in range(int(m[2]))])
  else:assert re.fullmatch(r'\w+',name);names.append(name)
assert len(names)==917 and len(fields)==434 and len(set(fields))==434
bits=[0]*29
for name in fields:
 i=names.index(name);bits[i//32]|=1<<(i%32)
table='static const uint32_t sentinel_bits[29]={'+','.join(hex(v) for v in bits)+'};\n'
head=head.replace('void probe817(',table+'void probe817(')
loop=' for(unsigned i=0;i<917;++i)if(sentinel_bits[i>>5]&(1u<<(i&31)))((uint32_t *)o)[i]=0xffffffff;\n'
out=(head+loop+tail).replace('static uint8_t cr(','static __attribute__((noinline)) uint8_t cr(').replace('static void cw(','static __attribute__((noinline)) void cw(')
with (K/'probe-bitmap-native.c').open('xb') as f:f.write(out.encode())
(K/'bitmap001.json').write_text(json.dumps(dict(source_only=True,fields=fields,field_indices=[names.index(f) for f in fields],bitmap=bits,groups=groups,hardware_tail_unchanged=True,qualification=False),indent=2)+'\n')
m=(K/'measure001.py').read_text().replace('measure001','measure002').replace("'probe-shared-native.c','probe.h'","'probe-shared-native.c','probe-bitmap-native.c','probe.h'")
a=m.index("for name,extra in ");z=m.index(':\n  p=O/name',a)
m=m[:a]+"for name,extra in [('bitmap-native',[])]"+m[z:]
a=m.index("str(K/('probe-native.c'");z=m.index(",'-o'",a)
m=m[:a]+"str(K/'probe-bitmap-native.c')"+m[z:]
(K/'measure002.py').write_bytes(m.encode())
print('Bitmap source prepared; equivalence pending')
