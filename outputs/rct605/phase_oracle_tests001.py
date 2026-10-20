"""Reject altered phase evidence in cached exports; never reopen a runtime."""
import hashlib,json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;out=K/'phase-oracle-tests001.json';assert not out.exists()
b=json.loads((K/'build002.json').read_text())
p=Path('C:/xwn605/pc001/cold1-002/files/xwn605/trace.txt')
text=p.read_text();lines=text.splitlines()
check=lambda t:validate(t,b['target_image_base'],b['target_image_size'])
positive=check(text)
idx=lambda kind:next(i for i,l in enumerate(lines) if l.startswith(kind+' '))
def change(i,f,v):
 a=lines.copy();s=a[i].split();s[f]=v;a[i]=' '.join(s);return '\n'.join(a)+'\n'
def omit(i):return '\n'.join(lines[:i]+lines[i+1:])+'\n'
ph=idx('PHASE');pe=idx('PHASE_END');pd=idx('PHASE_PENDING')
variants={
 'missing_phase':omit(ph),'duplicate_phase':'\n'.join(lines[:ph]+[lines[ph]]+lines[ph:])+'\n',
 'invalid_phase':change(ph,1,'00000002'),'false_count':change(ph,2,'0000001f'),
 'false_startup_skips':change(ph,3,'00000003'),'missing_deferred':omit(pd),
 'false_pending_depth':change(pd,2,'00000002'),'missing_phase_end':omit(pe),
 'false_end_phase':change(pe,1,'00000000'),'false_park_skips':change(pe,3,'00000003'),
}
# Move the phase marker before the last outstanding return, preserving all other lines.
ret=max(i for i in range(ph) if lines[i].startswith('RETURN '))
a=lines.copy();marker=a.pop(ph);a.insert(ret,marker)
variants['transition_with_pending_frame']='\n'.join(a)+'\n'
rejected=[]
for name,t in variants.items():
 try:check(t)
 except (AssertionError,ValueError,KeyError,UnicodeError,IndexError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Mutations of cached original-control evidence only.'),indent=2)+'\n')
print('605 phase oracle rejected all',len(rejected),'altered traces')
