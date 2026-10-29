"""Compact report-only sentinel initialization; preserve all hardware operations."""
from pathlib import Path
import re,hashlib,json
K=Path(__file__).resolve().parent
s=(K/'probe-native.c').read_text();cut=s.index(' for(unsigned i=0;i<7;++i)o->h_checked')
head,tail=s[:cut],s[cut:];fields=[]
def replace(m):
    fields.extend(reversed(re.findall(r'o->(\w+)',m[1])))
    return ''
head,n=re.subn(r'((?:o->\w+=)+)0xffffffff;',replace,head)
assert n>20 and len(fields)>100 and len(set(fields))==len(fields)
table='static const uint16_t sentinel_offsets[] = {\n'+''.join(
    ' (uint16_t)__builtin_offsetof(struct result806,'+f+'),\n' for f in fields)+'};\n'
head=head.replace('void probe806(',table+'void probe806(')
loop=' for(unsigned i=0;i<sizeof(sentinel_offsets)/sizeof(sentinel_offsets[0]);++i)\n  *(uint32_t *)((uint8_t *)o+sentinel_offsets[i])=0xffffffff;\n'
out=head+loop+tail
assert out[out.index(' for(unsigned i=0;i<7;++i)o->h_checked'):]==tail
p=K/'probe-compact-native.c';assert not p.exists();p.write_bytes(out.encode())
(K/'compact001.json').write_text(json.dumps(dict(source_only=True,physical_access=False,
    original_sha256=hashlib.sha256(s.encode()).hexdigest(),compact_sha256=hashlib.sha256(out.encode()).hexdigest(),
    fields=fields,assignment_groups=n,hardware_operation_tail_byte_exact=True,
    qualification='Pending actual-ELF equivalence and full native qualification'),indent=2)+'\n')
print('Compacted',len(fields),'sentinel fields;',n,'assignment groups; hardware tail exact')
