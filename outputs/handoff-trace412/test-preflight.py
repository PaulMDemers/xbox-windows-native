import ast,json,struct,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent
source=(K/'trace.py').read_text();tree=ast.parse(source)
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='translate')
calls=[];memory={}
def capture(a,n,label,physical=False):
    assert n==4 and physical and 0<=a<0x4000000;calls.append(a);return struct.pack('<I',memory[a])
g={'capture':capture,'struct':struct};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-translate','exec'),g)
f=g['translate'];regs={'CR0':0x80000001,'CR3':0x3000,'CR4':0x10};va=0x02000123
memory[0x3020]=0x9001;memory[0x9000]=0x86003
assert f(va,regs,'small')==0x86123 and calls==[0x3020,0x9000]
memory[0x3020]=0x01400081
assert f(va,regs,'large')==0x01400123
rejected=0
for changes,pde,pte in [({'CR0':1},0x9001,0x86003),({'CR4':0x20},0x9001,0x86003),({},0,0x86003),({},0x9001,0x86002),({'CR4':0},0x01400081,0)]:
    memory[0x3020]=pde;memory[0x9000]=pte
    try:f(va,dict(regs,**changes),'negative')
    except AssertionError:rejected+=1
    else:raise AssertionError('Invalid translation accepted')
xbe=Path('E:/xwn374/build001/default.xbe').read_bytes()
assert xbe[0x11f2:0x1205]==bytes.fromhex('ffe2fa0f20c025ffffff7f0f22c031c00f22d8')
assert xbe[0x1244:0x1258]==bytes.fromhex('bf00006002b900001000f3a4faea000060020800')
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
r=dict(passed=True,actual_translation_cases=2,rejected_translation_controls=rejected,original_checkpoint_opcodes_exact=True,paging_change_offset=12,source_sha256=hashlib.sha256(source.encode()).hexdigest(),scope='Host protocol preflight, not runtime evidence')
with (K/'preflight001.json').open('x',encoding='utf-8') as out:json.dump(r,out,indent=2);out.write('\n')
print(json.dumps(r))
