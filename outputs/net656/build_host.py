"""Fresh, leased host-only compile/test; no implicit deployment or launch."""
import argparse,datetime,hashlib,json,os,re,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
p=argparse.ArgumentParser();p.add_argument('attempt');a=p.parse_args()
assert re.fullmatch(r'host[0-9]{3}',a.attempt)
B=Path('/mnt/c/xwn656')/a.attempt;out=K/(a.attempt+'.json')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='preflight',physical_access=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05);B.mkdir(parents=True);(B/'source').mkdir();(B/'tmp').mkdir()
 for name in ('nic.h','nic.c','test.c','build_host.py'):(B/'source'/name).write_bytes((K/name).read_bytes())
 r['source_pins']={p.name:sha(p) for p in (B/'source').iterdir()}
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc);env=dict(os.environ,TMPDIR=str(B/'tmp'))
 def run(name,args):
  r.setdefault('commands',[]).append([str(x) for x in args]);save()
  x=subprocess.run(args,capture_output=True,timeout=90,env=env)
  (B/(name+'.stdout')).write_bytes(x.stdout);(B/(name+'.stderr')).write_bytes(x.stderr)
  assert x.returncode==0,(name,x.returncode)
  return x.stdout
 run('compile',[str(cc),'-std=c99','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',str(B/'source/nic.c'),str(B/'source/test.c'),'-o',str(B/'test')])
 r['tests']=json.loads(run('test',[str(B/'test')]))
 run('compile-i386',[str(cc),'-m32','-std=c99','-Wall','-Wextra','-Werror','-O2','-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-c',str(B/'source/nic.c'),'-o',str(B/'nic-i386.o')])
 assert run('undefined',['nm','-u',str(B/'nic-i386.o')])==b''
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()};r['status']='pass'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(status=r['status'],tests=r.get('tests'))))
