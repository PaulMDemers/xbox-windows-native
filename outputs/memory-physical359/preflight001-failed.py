"""Actual path functions under rejected/mocked I/O; no physical access."""
import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'host001.json';assert not dest.exists()
sys.path.insert(0,str(K));import physical as p
checks=0
def yes(fn,*a):
 global checks
 checks+=1;fn(*a)
def no(fn,*a):
 global checks
 checks+=1
 try:fn(*a)
 except AssertionError:return
 raise AssertionError(a)
for case in ['control001','candidate001']:
 for path in [p.START,p.DLL,'/E/xwnmemory359'+case+'/runner.exe']:yes(p.write_path,path,case)
 for path in ['/C/winnt/test','/E/../C/test','/F/winnt/test','/E/xwnmemory359other/runner.exe','/E/xwnmemory359'+case+'/unknown.exe','/E/xwnmemory359'+case+'/../bad'] :no(p.write_path,path,case)
for path in ['/C','/C/file','/E/../C/file','/E//file','/E/\\C'] :no(p.read_path,path)
for n in K.glob('*.py'):ast.parse(n.read_text())
s=(K/'physical.py').read_text();body=s[s.index('def collect('):s.index("if __name__")]
assert body.index('store(f,START,normal,case)')<body.index('current=fetch(f,DLL)')<body.index('store(f,DLL,original,case)')<body.index('for name in LOGS:')
assert s.count("f.sendcmd(r['command'])")==1 and "memory-runtime355" in s
dest.write_text(json.dumps(dict(passed=True,path_cases=checks,restore_order='startup,preserve tested driver,original driver,remaining evidence',only_new_E_helpers_and_START_DLL_writes=True,no_console_access=True,modeled_io=True,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.py')}),indent=2)+'\n')
print(checks,'physical path/restore contract checks')
