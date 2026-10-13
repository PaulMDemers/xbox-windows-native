import ast,hashlib,json,struct
from pathlib import Path
from protocol import paired,surface
K=Path(__file__).resolve().parent;dest=K/'protocol-tests001.json';assert not dest.exists();checks=0
for cleanup in [0,24]:
    for address in [0x0040543f,0xbf801234]:
        call=dict(return_address=address,expected_return_sp=0x120004+cleanup,thread=0x82111110,process=0x82222220,returned=False)
        args=[call['return_address'],call['expected_return_sp'],call['thread'],call['process']]
        assert paired(call,*args);checks+=1
        for index in range(4):
            for bit in range(32):
                bad=args.copy();bad[index]^=1<<bit;assert not paired(call,*bad);checks+=1
        call['returned']=True;assert not paired(call,*args);checks+=1
for typ in [0,1]:
    for stride in [128,-128,7680]:
        v=[0x100,0x200,0x300,0x400,1920,1080,8294400,0x81000000,0x81000000,stride&0xffffffff,3,6,typ,0]
        raw=struct.pack('<12I2H',*v);s=surface(raw,0x82300000)
        assert s['stride']==stride and s['type']==typ and s['width']==1920 and s['format']==6;checks+=1
        for n in [0,1,48,51,53]:
            try:surface((raw+bytes(8))[:n],0x82300000)
            except AssertionError:checks+=1
            else:raise AssertionError('Invalid surface length accepted')
source=(K/'trace.py').read_text();tree=ast.parse(source)
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='g' and n.func.attr=='write' for n in ast.walk(tree));checks+=1
for text in ['range(512)','+600','armed_breakpoints_remaining','Qqemu.PhyMemMode:0',"id==12+len(completed)","len(active['calls'])<128"]:assert text in source;checks+=1
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
r=dict(passed=True,checks=checks,scope='Actual pure surface and thread/process/frame-return decoder tests plus bounded/write-free source checks; not live GDB or guest proof.',inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),K/'protocol.py',K/'trace.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print(r['checks'],'host trace checks passed')
