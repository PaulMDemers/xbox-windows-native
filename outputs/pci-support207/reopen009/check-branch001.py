"""Exercise trace dispatch with a nonclass open, class open and class helper entry."""
import ast,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
def exercise(path,label,module):
    tree=ast.parse(path.read_text())
    branch=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=="label.endswith('_enable_enter')")
    ns=dict(label=label,g=type('FakeRemote',(),{'read':lambda self,a,n:struct.pack('<5I',0x82403000,1,2,3,4)})(),regs={'esp':0x90000000,'ebp':0x90000040},struct=struct,serial=0,utc=lambda:'mock',optional=lambda *args:None,u32=lambda *args:0,uni=lambda *args:'mock',file_info=lambda *args:None,device=lambda *args:None,stack_observation=lambda *args:None,identity={},locate=lambda a:{'module':module},a=0x82403000,K=0x82402000,plan={'providers':{'ntoskrnl.exe':{'image_size':0x200000}}},r={'calls':[],'open_callers':[]},pending={},thread=1,pin=lambda *args:None,extras=lambda *args:None)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[branch],type_ignores=[])),str(path),'exec'),ns)
    return len(ns['r']['calls'])
old=k.parent/'reopen008/trace.py';new=k/'trace.py'
try:exercise(old,'open_enter','ntoskrnl.exe')
except NameError as e:old_error=str(e)
else:raise AssertionError('The original dispatch failure must reproduce')
rows=[]
for label,module,count in [('open_enter','ntoskrnl.exe',0),('open_enter','kbdclass.sys',1),('kbd_enable_enter','kbdclass.sys',1)]:
    actual=exercise(new,label,module);assert actual==count
    rows.append(dict(label=label,module=module,expected=count,observed=actual))
r=dict(passed=True,old_error=old_error,cases=rows,old_trace_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),new_trace_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits='Host dispatch regression test only, no guest or stack-unwind qualification.')
dest=k/'branch-review001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print('Original NameError reproduced; three corrected dispatch paths pass')
