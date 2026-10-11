"""Synthetic transport/lifetime controls, never real GL/guest coverage."""
import importlib.util,json,struct,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('watch',k/'analyze-watch.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def blob(u,stage):
    h=[0x3936324e5758,269,stage,u,u+1,100+u,30+u,2,22,0,4096+u*64,64,0,0,4,4,0x8058,64,8,1,0,55,66,1]
    return struct.pack('<24Q',*h)+bytes([u])*8+bytes(range(64))+bytes(range(64))
units={u:dict(binding_identity=100+u,gl_texture=30+u) for u in range(4)}
with tempfile.TemporaryDirectory() as td:
    p=Path(td)
    def reset():
        for f in p.iterdir():f.unlink()
        for u in range(4):
            for stage in range(2):(p/f'unit-{u}-stage-{stage}.bin').write_bytes(blob(u,stage))
        (p/'event-000.txt').write_text('seq=0 kind=1 unit=0 identity=0 code=0 thread=55\n')
        for u in range(4):(p/f'event-{u+1:03d}.txt').write_text(f'seq={u+1} kind=2 unit={u} identity={100+u} code=2 thread=55\n')
    reset();assert m.inspect(p,units,55,66,0)['all_four_unchanged']
    rejected=0
    for field,value in [(0,0),(1,268),(4,55),(5,0),(6,0),(11,m.MAX+1),(13,4097),(17,0),(18,257),(19,0),(20,1),(21,56),(22,67),(23,0)]:
        reset();f=p/'unit-0-stage-1.bin';raw=bytearray(f.read_bytes());struct.pack_into('<Q',raw,field*8,value);f.write_bytes(raw)
        try:m.inspect(p,units,55,66,0)
        except AssertionError:rejected+=1
        else:raise AssertionError(field)
    for mode in range(5):
        reset()
        if mode==0:(p/'event-002.txt').write_text('seq=2 kind=2 unit=0 identity=100 code=2 thread=55\n')
        if mode==1:(p/'event-001.txt').write_text('seq=1 kind=9 unit=0 identity=100 code=1 thread=55\n')
        if mode==2:(p/'unit-1-stage-1.bin').unlink()
        if mode==3:(p/'event-000.txt').unlink()
        if mode==4:(p/'event-001.txt').write_text('seq=1 kind=4 unit=0 identity=100 code=0 thread=55\n')
        try:m.inspect(p,units,55,66,0)
        except AssertionError:rejected+=1
        else:raise AssertionError(mode)
    reset();f=p/'unit-0-stage-1.bin';raw=bytearray(f.read_bytes());raw[-1]^=1;f.write_bytes(raw)
    assert not m.inspect(p,units,55,66,0)['all_four_unchanged']
    reset()
    for u in range(4):(p/f'unit-{u}-stage-1.bin').unlink();(p/f'event-{u+1:03d}.txt').unlink()
    assert not m.inspect(p,units,55,66,0)['all_four_actual_reuse']
r={'passed':True,'synthetic_rejected':rejected,'byte_mutation_fails_equality':True,'no_reuse_fails_coverage':True,'actual_gl':False}
dest=k/'parser-tests001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(r)
