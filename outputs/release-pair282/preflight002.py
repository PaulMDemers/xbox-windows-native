"""Fresh bounded controller tests. Explicit models, never new guest evidence."""
import ast,copy,hashlib,json,struct,traceback
from pathlib import Path
import checks,transport,proof
k=Path(__file__).resolve().parent;dest=k/'preflight002.json';assert not dest.exists()
capsule=Path('E:/Codex-archive/xbox-windows-native/pair282-preflight002');capsule.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p in list(k.glob('*.py'))+list(k.glob('*.ps1')):(capsule/p.name).write_bytes(p.read_bytes())
rejected=0
def reject(fn):
 global rejected
 try:fn()
 except (AssertionError,KeyError,IndexError,struct.error):rejected+=1
 else:raise AssertionError('Invalid controller input accepted')
def text(records,groups,candidate,ending):
 n=dict(version=281,state=5 if ending else 3,reason=0,candidate=int(candidate),mask=15 if candidate else 0,armed=1,post=1,sealed=int(ending),native_grant=0)
 for i in range(2):
  n[f'record{i}_present']=int(not i or ending)
  if not i or ending:n.update({f'record{i}_{j}':v for j,v in enumerate(records[i])})
 for stage,g in enumerate(groups,1):
  n[f's{stage}_state']=0 if stage==3 and not ending else 5
  if stage==3 and not ending:continue
  n.update({f's{stage}_{q}':0 for q in ['reason','overflow','accounting','shader_unknown']})
  n[f's{stage}_rows']=len(g);n[f's{stage}_pages']=(len(g)+255)//256
 return ' '.join(f'{a}={b}' for a,b in n.items())
r=dict(passed=False,host_only=True,guest_launched=False,models=['280 actual orchestration output from CPU/GL models','278 closed snapshot/terminal replay with explicit synthetic post-release fields, not new guest evidence'])
try:
 for p in k.glob('*.py'):ast.parse(p.read_text())
 for mode in range(2):
  b=Path(f'E:/Codex-archive/xbox-windows-native/release280-worker004/mode{mode}.bin').read_bytes();records,groups=transport.read(b)
  for ending in [False,True]:
   s=text(records,groups,bool(mode),ending);checks.report(s,bool(mode),ending)
   tokens=s.split()
   for i,word in enumerate(tokens):
    key,value=word.split('=')
    reject(lambda i=i:checks.report(' '.join(tokens[:i]+tokens[i+1:]),bool(mode),ending))
    reject(lambda word=word:checks.report(s+' '+word,bool(mode),ending))
   reject(lambda:checks.report(s,not bool(mode),ending));reject(lambda:checks.report(s,bool(mode),not ending))
  checks.pair(records[:1],groups[:2],bool(mode))
  for stage in range(2):
   for kind,col in [(17,3),(66,4),(67,4),(71,2),(71,3),(72,2)]:
    m=copy.deepcopy(groups[:2]);v=next(v for v in m[stage] if v[0]==kind)
    if kind==71 and col==3:v[col]=0
    else:v[col]^=1
    reject(lambda:checks.pair(records[:1],m,bool(mode)))
  reject(lambda:checks.pair(records[:1],groups[:2],not bool(mode)))
 # Pixel oracle remains independent. Replay old bytes only as test input.
 prior=k.parent/'texture-boundary278/emu001';t=json.loads((prior/'trace.json').read_text());root=Path('E:/xwn278/emu001')
 real=json.loads((prior/'reuse-proof.json').read_text());worker=int(next(v.split('=')[1] for v in t['initial_report'].split() if v.startswith('worker=')))
 context=int(real['graphs'][0]['extension']['native_contexts']['1'])
 for mode in range(2):
  modelroot=capsule/('model'+str(mode));(modelroot/'watch').mkdir(parents=True)
  for u in range(4):
   for stage in (0,1):(modelroot/f'watch/unit-{u}-stage-{stage}.bin').write_bytes((root/f'watch/unit-{u}-stage-{stage}.bin').read_bytes())
   post=bytearray((root/f'watch/unit-{u}-stage-0.bin').read_bytes());struct.pack_into('<Q',post,16,2);struct.pack_into('<Q',post,56,1 if mode else 2)
   (modelroot/f'watch/unit-{u}-stage-2.bin').write_bytes(post)
  term=bytearray((root/'watch/terminal273.bin').read_bytes())
  if mode:
   # Rebuild modeled candidate ordering: four release DEC then four real binds.
   for u in range(4):struct.pack_into('<Q',term,128+u*160+64,5+u)
   for i in range(4):
    at=768+64*i;slot=struct.unpack_from('<Q',term,at+32)[0]
    struct.pack_into('<Q',term,at,1+slot);struct.pack_into('<Q',term,at+40,2);struct.pack_into('<Q',term,at+48,1+slot)
  (modelroot/'watch/terminal273.bin').write_bytes(term)
  rec=[0]*16;rec[10]=worker
  initial=dict(records=[rec],graphs=[dict(extension=dict(native_contexts={'1':context}))],unbound_edges=dict(selected=[dict(identity=x['identity'],gl_name=x['gl_name']) for x in real['captures']]))
  final=dict(records=[rec,rec],graphs=initial['graphs'])
  proof.initial_snapshots(modelroot,t,initial,bool(mode));proof.resumed(modelroot,t,initial,final,bool(mode))
  p=modelroot/'watch/unit-0-stage-2.bin';original=p.read_bytes();m=bytearray(original);struct.pack_into('<Q',m,56,99);p.write_bytes(m)
  reject(lambda:proof.initial_snapshots(modelroot,t,initial,bool(mode)));p.write_bytes(original)
 for u in range(4):
  data=(root/f'watch/unit-{u}-stage-0.bin').read_bytes();phys=t['checkpoints'][0]['state_header'][18+u]
  proof.snapshot(data,u,0,phys,worker,context)
  for off in range(len(data)-1024,len(data)):
   m=bytearray(data);m[off]^=1;reject(lambda:proof.snapshot(bytes(m),u,0,phys,worker,context))
  for col in [0,1,2,3,5,10,11,12,13,14,15,16,17,19,20,21,22,23]:
   m=bytearray(data);struct.pack_into('<Q',m,col*8,0 if col not in [2,3,12,13,20] else 999)
   # Identity is linked by surrounding proof, not snapshot parser alone.
   if col==5:continue
   reject(lambda:proof.snapshot(bytes(m),u,0,phys,worker,context))
 assert (k/'atomic_json.py').read_bytes()==(k.parent/'surface-bridge260/atomic_json.py').read_bytes()
 build=json.loads((k.parent/'release-runtime281/source-review.json').read_text());assert build['passed']
 r.update(passed=True,negative_controls=rejected,actual_compiled_sha256=build['compiled_sha256'])
except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
r['files']={p.name:sha(p) for p in capsule.iterdir() if p.is_file()}
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:v for a,v in r.items() if a!='files'},indent=2));assert r['passed']
