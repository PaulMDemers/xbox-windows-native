"""Reject altered lifetime evidence using the exact cold control trace."""
import hashlib,json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;out=K/'lifetime-oracle-tests001.json';assert not out.exists()
b=json.loads((K/'build002.json').read_text());p=Path('C:/xwn610/pc001/cold1-002/files/xwn610/trace.txt')
text=p.read_text();lines=text.splitlines();validate(text,b['target_image_base'],b['target_image_size'])
def first(kind):return next(i for i,l in enumerate(lines) if l.startswith(kind+' '))
def change(i,field,value):
 a=lines.copy();v=a[i].split();v[field]=value;a[i]=' '.join(v);return '\n'.join(a)+'\n'
def remove(i):return '\n'.join(lines[:i]+lines[i+1:])+'\n'
ri=first('RETIRE');qi=next(i for i,l in enumerate(lines) if l.startswith('QUIESCENT 62000000'))
ui=next(i for i,l in enumerate(lines) if l.startswith('UNLOAD 62000000'))
li=[i for i,l in enumerate(lines) if l.startswith('LIFETIME 62000000')]
bi=first('BPOWNER');ci=first('BPCODE')
code_f8=next(i for i,l in enumerate(lines) if l.startswith('BPCODE ') and l.endswith('000000f8'))
variants={
 'missing_retire':remove(ri),'wrong_retire_generation':change(ri,2,'ffffffff'),
 'wrong_retire_address':change(ri,3,'00000000'),'duplicate_retire':'\n'.join(lines[:ri]+[lines[ri]]+lines[ri:])+'\n',
 'missing_quiescent':remove(qi),'false_quiescent_generation':change(qi,2,'ffffffff'),
 'unknown_unload':change(ui,1,'63000000'),'missing_unload':remove(ui),
 'reused_generation':change(li[1],2,lines[li[0]].split()[2]),
 'wrong_owner_generation':change(bi,2,'ffffffff'),'missing_owner':remove(bi),
 'missing_original_byte':remove(ci),'trap_original_byte':change(ci,3,'000000cc'),
 'stale_byte_from_previous_image':change(code_f8,3,'00000090'),
 'missing_lifetime':remove(li[0]),'false_image_size':change(li[0],3,'00000001'),
}
results=[]
for name,value in variants.items():
 rejected=False
 try:validate(value,b['target_image_base'],b['target_image_size'])
 except (AssertionError,KeyError,ValueError,IndexError,TypeError):rejected=True
 results.append(dict(name=name,rejected=rejected));assert rejected,name
out.write_text(json.dumps(dict(passed=True,positive=True,trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),negative_cases=results),indent=2)+'\n')
print('610 lifetime trace mutations rejected:',len(results))
