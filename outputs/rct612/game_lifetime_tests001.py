"""Adversarial lifetime records in the actual cold game trace."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'game-lifetime-tests001.json';assert not out.exists()
assert json.loads((K/'review001.json').read_text())['passed']
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
from analyze_trace001 import analyze
pe=pefile.PE('C:/xwn566/transfer002/game/RCT.EXE')
p=Path('C:/xwn612/pc001/cold1-002/files/xwn612/trace.txt');text=p.read_text();lines=text.splitlines()
check=lambda t:analyze(t,pe.OPTIONAL_HEADER.ImageBase,pe.OPTIONAL_HEADER.SizeOfImage)
check(text)
ri=next(i for i,l in enumerate(lines) if l.startswith('RETIRE '))
qi=max(i for i,l in enumerate(lines[:ri]) if l.startswith('QUIESCENT '))
ui=next(i for i in range(ri,len(lines)) if lines[i].startswith('UNLOAD '))
def change(i,f,value):
 a=lines.copy();v=a[i].split();v[f]=value;a[i]=' '.join(v);return '\n'.join(a)+'\n'
def remove(i):return '\n'.join(lines[:i]+lines[i+1:])+'\n'
variants={'missing_retirement':remove(ri),'wrong_generation':change(ri,2,'ffffffff'),
 'wrong_address':change(ri,3,'00000000'),'missing_quiescent':remove(qi),
 'unknown_unload':change(ui,1,'00000000'),
 'duplicate_retirement':'\n'.join(lines[:ri]+[lines[ri]]+lines[ri:])+'\n'}
rejected=[]
for name,value in variants.items():
 try:check(value)
 except (AssertionError,KeyError,ValueError,IndexError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest()),indent=2)+'\n')
