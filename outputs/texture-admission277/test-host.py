"""Freeze one host-only proposal and run exact lifecycle bodies plus admission.
The real276 data is retained; absent second CPU boundary/clock are model-only.
"""
import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;prior=k.parent/'callback-inventory276'
dest=k/'host001.json';assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/admission277-host001');out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=['test-host.py','test.c','admission.h','clock.c','patch-clock.py']
for n in inputs:(out/n).write_bytes((k/n).read_bytes())
source=Path('E:/Codex-archive/xbox-windows-native/callback276-build003/source/system/physmem.c')
pins=json.loads((prior/'renderer-source-pins003.json').read_text());assert sha(source)==pins['system/physmem.c']
original=source.read_text();(out/'original-physmem.c').write_bytes(source.read_bytes())
spec=importlib.util.spec_from_file_location('patch277',k/'patch-clock.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
proposed=mod.apply(original);(out/'proposed-physmem.c').write_text(proposed)
assert proposed.replace((k/'clock.c').read_text()+'\n','').replace('    x277_clock_advance(cpu);\n','')==original
def function(s,name):
    pos=s.index(name);a=s.rfind('static void ',0,pos);assert a>=0
    brace=s.index('{',pos);level=1;b=brace+1
    while level:
        level+=(s[b]=='{')-(s[b]=='}');b+=1
    return s[a:b]
insert=function(proposed,'do_mem_access_callback_insert(');remove=function(proposed,'do_mem_access_callback_remove_by_ref(')
for name,body in [('do_mem_access_callback_insert(',insert),('do_mem_access_callback_remove_by_ref(',remove)]:
    assert body.replace('    x277_clock_advance(cpu);\n','')==function(original,name)
# Pinned real QEMU queue macros; not a replacement queue implementation.
queue='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility'
p=subprocess.run(['wsl','-d','Ubuntu','--','cat','/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet/include/qemu/queue.h'],capture_output=True,timeout=20);assert p.returncode==0
(out/'queue.h').write_bytes(p.stdout)
analysis=json.loads((prior/'emu001/inventory-analysis.json').read_text())
trace=json.loads((prior/'emu001/trace.json').read_text());h=trace['checkpoints'][0]['state_header']
rows=[]
for rec in trace['initial_pages']:
    path=prior/'emu001'/rec['file'];assert sha(path)==rec['sha256']
    rows.extend(list(map(int,v.split(':'))) for v in re.findall(r'(?<!\w)r\d+=([0-9:]+)',path.read_text()))
units={r[1]:r[2] for r in rows if r[0]==3};bindings={r[1]:r for r in rows if r[0]==4}
callbacks=[];surfaces=[];textures=[]
inventory=trace['callback_inventory_report']
actual=[list(map(int,x.split(':'))) for x in re.findall(r' c\d+=([0-9:]+)',inventory)]
header=analysis['actual_cpu_header'];base=actual[0][6]-actual[0][1]
for c,s in zip(actual,analysis['matched_callbacks']):
    assert c[0]==s['callback'];callbacks.append('{'+','.join(str(x)+'ULL' for x in c)+'}')
    surfaces.append('{'+','.join(str(s[x])+'ULL' for x in ['surface','callback','start','bytes','gl_texture','flags','binding_roles'])+'}')
for i in range(4):
    identity=units[i];b=bindings[identity]
    cache=[r for r in rows if r[0]==2 and r[2]==identity];assert len(cache)==1
    assert cache[0][3:7]==[h[18+i],512,0,0]
    textures.append('{'+','.join(str(x)+'ULL' for x in [identity,b[3],h[10+i],4096,h[18+i],512,0,0,2,1,1])+'}')
# Model-only second checkpoint times and clock. The first CPU tuples, graph,
# ranges and texture identities come from276; this fixture is NOT runtime proof.
c='{.epoch=%d,.thread='+str(header['thread'])+'ULL,.when=%d,.clock=100,.done=1,.count=4,.callbacks={'+','.join(callbacks)+'}}'
g='{.complete=1,.count=4,.surfaces={'+','.join(surfaces)+'}}'
fixture='static const X277Proof fixture={.stage=1,.worker='+str(header['worker'])+'ULL,.device='+str(header['device'])+'ULL,.region='+str(actual[0][5])+'ULL,.function='+str(actual[0][4])+'ULL,.ram_base='+str(base)+'ULL,.ram_bytes=67108864,.started=1,.finished=4,.deadline=10,.render_context=65538,.display_context=65539,.cpu_stopped=1,.frontend_closed=1,.pfifo_halted=1,.render_fenced=1,.display_fenced=1,.get_equals_put=1,.textures={'+','.join(textures)+'},.cpu={'+c%(1,2)+','+c%(2,3)+'},.graph={'+g+','+g+'}};\n'
(out/'fixture.h').write_text(fixture)
s=(k/'test.c').read_text().replace('/* ACTUAL_CLOCK */',(k/'clock.c').read_text()).replace('/* ACTUAL_INSERT */',insert).replace('/* ACTUAL_REMOVE */',remove)
(out/'actual-test.c').write_text(s)
base='/mnt/e/Codex-archive/xbox-windows-native/admission277-host001'
r=dict(passed=False,guest_launched=False,renderer_installed=False,release_installed=False,
    scope='Host-only exact CPU insert/unlink bodies and proposed admission; actual276 tuples with explicitly modeled missing clocks/second acknowledgments/context gates',
    original_functions_reconstructed=True,old276_qualification_unchanged=True)
try:
    p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
    r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
    p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=120)
    r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0
    r['passed']=True
except BaseException as e:r['error']=repr(e)
r['files']={str(p):sha(p) for p in out.iterdir() if p.is_file()}
r['actual276_inputs']={str(p):sha(p) for p in [prior/'emu001/inventory-analysis.json',prior/'emu001/trace.json',source]}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a not in ['files','actual276_inputs']},indent=2));assert r['passed']
