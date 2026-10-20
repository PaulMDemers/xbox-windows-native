"""Reject false/missing absent-output evidence in the exported actual control."""
import hashlib,json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;out=K/'absent-tests001.json';assert not out.exists()
b=json.loads((K/'build002.json').read_text());p=Path('C:/xwn607/pc001/cold1-002/files/xwn607/trace.txt')
text=p.read_text();lines=text.splitlines();check=lambda t:validate(t,b['target_image_base'],b['target_image_size'])
check(text);absent=[i for i,l in enumerate(lines) if l.startswith('OUTPUT_ABSENT ')];assert len(absent)==3
i=absent[0]
def change(index,field,value):
 a=lines.copy();s=a[index].split();s[field]=value;a[index]=' '.join(s);return '\n'.join(a)+'\n'
normal=next(j for j,l in enumerate(lines) if l.startswith('OUTPUT ') and l.split()[2]=='00000004')
parts=lines[normal].split();false=lines.copy();false[normal]='OUTPUT_ABSENT '+parts[1]+' 00000004 00000000'
fake=lines.copy();fake[i]=lines[i].replace('OUTPUT_ABSENT','OUTPUT')+' 12345678'
variants={
 'missing_absent':'\n'.join(lines[:i]+lines[i+1:])+'\n',
 'duplicate_absent':'\n'.join(lines[:i]+[lines[i]]+lines[i:])+'\n',
 'wrong_api':change(i,2,'00000005'),
 'nonzero_address':change(i,3,'00000001'),
 'unknown_call':change(i,1,'ffffffff'),
 'absent_for_nonnull_argument':'\n'.join(false)+'\n',
 'invented_bits_pointer':'\n'.join(fake)+'\n',
}
rejected=[]
for name,t in variants.items():
 try:check(t)
 except (AssertionError,KeyError,ValueError,IndexError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,absent_records=3,rejected=rejected,trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest()),indent=2)+'\n')
print('607 three actual absent outputs; seven altered traces rejected')
