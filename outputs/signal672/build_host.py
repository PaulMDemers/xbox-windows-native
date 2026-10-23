"""Fresh leased sanitizer build of the signal protocol; no console access."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
B=Path('/mnt/c/xwn672/host001');out=K/'host001.json'
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,commands=[],source_pins={})
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05);B.mkdir(parents=True);S=B/'source';S.mkdir()
 inputs=[K/n for n in ['signal672.c','signal672.h','test.c','build_host.py']]
 inputs += [W/'outputs/terminal669/phase.h',W/'outputs/net656/nic.h']
 inputs += [Path('/mnt/c/xwn671/source001/drivers/diag657')/n for n in ['indication.c','indication.h']]
 for p in inputs:
  (S/p.name).write_bytes(p.read_bytes());r['source_pins'][str(p)]=sha(p)
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc)
 def run(name,args):
  r['commands'].append([str(a) for a in args]);save()
  v=subprocess.run(args,capture_output=True,timeout=120)
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr)
  assert v.returncode==0,(name,v.returncode)
  return v.stdout
 run('compile',[str(cc),'-std=c99','-O1','-Wall','-Wextra','-Werror','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',str(S/'signal672.c'),str(S/'indication.c'),str(S/'test.c'),'-o',str(B/'test')])
 r['tests']=json.loads(run('test',[str(B/'test')]))
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()};r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],tests=r.get('tests'))))
