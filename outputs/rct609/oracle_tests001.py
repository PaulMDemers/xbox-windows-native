"""Reject altered cached game evidence; no new runtime."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'oracle-tests001.json';assert not out.exists()
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
from analyze_trace001 import analyze
pe=pefile.PE('C:/xwn566/transfer002/game/RCT.EXE')
p=Path('C:/xwn609/pc001/cold1-002/files/xwn609/trace.txt');text=p.read_text();lines=text.splitlines()
check=lambda t:analyze(t,pe.OPTIONAL_HEADER.ImageBase,pe.OPTIONAL_HEADER.SizeOfImage)
check(text)
idx=lambda kind:next(i for i,l in enumerate(lines) if l.startswith(kind+' '))
def change(i,f,v):
 a=lines.copy();s=a[i].split();s[f]=v;a[i]=' '.join(s);return '\n'.join(a)+'\n'
def omit(i):return '\n'.join(lines[:i]+lines[i+1:])+'\n'
ph=idx('PHASE');di=idx('DIB');ret=idx('RETURN')
variants={
 'missing_phase':omit(ph),'duplicate_phase':'\n'.join(lines[:ph]+[lines[ph]]+lines[ph:])+'\n',
 'invalid_phase':change(ph,1,'00000002'),'missing_header':omit(di),
 'wrong_header_pointer':change(di,2,'00000000'),'wrong_stride':change(di,5,'00000001'),
 'missing_return':omit(ret),'wrong_return_stack':change(ret,5,'00000000'),
 'missing_end':omit(len(lines)-1),'missing_phase_end':omit(idx('PHASE_END')),
}
rejected=[]
for name,t in variants.items():
 try:check(t)
 except (AssertionError,ValueError,KeyError,UnicodeError,IndexError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Actual game-trace mutations; does not create new game observations.'),indent=2)+'\n')
print('606 positive trace and ten rejection controls passed')
