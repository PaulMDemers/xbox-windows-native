import hashlib,json,struct,subprocess
from pathlib import Path
import decode
k=Path(__file__).resolve().parent;dest=k/'graph-host001.json';assert not dest.exists()
out=Path('E:/Codex-archive/xbox-windows-native/boundary278-graph001');out.mkdir(exist_ok=False)
source=(k/'adapter.c').read_text()
def function(name):
 p=source.index(name+'(');a=source.rfind('static ',0,p);b=source.index('{',p)+1;n=1
 while n:n+=(source[b]=='{')-(source[b]=='}');b+=1
 return source[a:b]
for n in ['test-graph.py','test-graph.c','admission.h','adapter.c','decode.py']:(out/n).write_bytes((k/n).read_bytes())
for n in ['fixture.h','queue.h']:(out/n).write_bytes((Path('E:/Codex-archive/xbox-windows-native/admission277-host002')/n).read_bytes())
(out/'actual-test.c').write_text((k/'test-graph.c').read_text().replace('/* ACTUAL_FUNCTIONS */',function('x278_parse')+'\n'+function('x278_graph')))
base='/mnt/e/Codex-archive/xbox-windows-native/boundary278-graph001'
r=dict(passed=False,guest_launched=False,actual_functions=['x278_parse','x278_graph'],models=['live QEMU surface/cache objects','GL names'],independent_scalar_decoder=True)
try:
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--','gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',base+'/actual-test.c','-o',base+'/test'],capture_output=True,timeout=60)
 r.update(compile_exit=p.returncode,compile_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 p=subprocess.run(['wsl','-d','Ubuntu','-u','root','--',base+'/test'],capture_output=True,timeout=60)
 r.update(test_exit=p.returncode,test_output=(p.stdout+p.stderr).decode());assert p.returncode==0
 data=Path('E:/Codex-archive/xbox-windows-native/boundary278-worker001/rows.bin').read_bytes();(out/'rows.bin').write_bytes(data)
 rows=[list(x) for x in struct.iter_unpack('<8Q',data)];assert decode.validate(rows,2)['callbacks']==4
 mutations=[]
 for index,row in enumerate(rows):
  if row[0] not in [17,64,65,66,67,68,69,70]:continue
  mutations.append(rows[:index]+rows[index+1:]);mutations.append(rows+[row])
  columns={17:[1,3,4,5,6,7],64:[1,2,3,4,5,6,7],65:[1,2,3,4,5,6,7],66:[1,2,3,4,5,6,7],67:[1,4,5,6,7],68:[1,2,3,4,5,6,7],69:[1,2,3,4,5,6,7],70:[1,2,3,4,5,6,7]}[row[0]]
  for col in columns:
   m=[r.copy() for r in rows];m[index][col]^=1;mutations.append(m)
 for m in mutations:
  try:decode.validate(m,2)
  except (AssertionError,KeyError):pass
  else:raise AssertionError('Unsafe proof mutation accepted')
 r.update(passed=True,proof_rows=len(rows),transport_mutations_rejected=len(mutations),transport_scope='278 complete scalar sub-proof; external native and full texture graph linkage remain separate controller requirements')
except BaseException as e:r['error']=repr(e)
r['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a!='files'},indent=2));assert r['passed']
