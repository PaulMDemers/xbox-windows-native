"""Validate explicit RAM-field bridge against actual pinned651 types, no hook."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];S=Path('/mnt/c/xwn651/source001');O=Path('/mnt/c/xwn652/bridge001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'bridge001.json').exists()
r=dict(passed=False,physical_access=False,native_hook_installed=False)
def save():(K/'bridge001.json').write_text(json.dumps(r,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(O,20.02)
 r['headers']={}
 for n in ['xwn_hd_adapter.h','xwn_hd_profile.h','trace649.h','readback651.h']:
  p=S/'drivers/video'/n
  assert subprocess.check_output(['git','-C',str(S),'show',':drivers/video/'+n],timeout=15)==p.read_bytes()
  r['headers'][n]=sha(p)
 for n,h in json.loads((K/'host001.json').read_text())['source_pins'].items():assert sha(K/n)==h
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)==json.loads((K/'host001.json').read_text())['compiler_sha256']
 r['source_pins']={n:sha(K/n) for n in ['bridge.c','test-bridge.c','bridge_test.py']}
 O.mkdir(parents=True);(O/'tmp').mkdir();env=dict(os.environ,TMPDIR=str(O/'tmp'))
 base=[str(cc),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(S/'drivers/video')]
 # Only unused functions in the existing readback651 header are suppressed.
 def run(name,args):
  p=subprocess.run(args,capture_output=True,timeout=60,env=env)
  (O/(name+'.stdout')).write_bytes(p.stdout);(O/(name+'.stderr')).write_bytes(p.stderr)
  assert p.returncode==0 and not p.stderr,(name,p.stderr.decode());return p.stdout.decode()
 run('compile',base+['-fsanitize=address,undefined','-fno-pie','-no-pie',str(K/'bridge.c'),str(K/'receipt.c'),str(K/'test-bridge.c'),'-o',str(O/'test-bridge')])
 r['host']=json.loads(run('test',[str(O/'test-bridge'),str(O/'synthetic-record.bin')]))
 assert (O/'synthetic-record.bin').read_bytes()==Path('/mnt/c/xwn652/host001/synthetic-record.bin').read_bytes()
 r['independent_oracle_bytes_match']=True
 run('i386',base+['-m32','-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-fno-stack-protector','-c',str(K/'bridge.c'),'-o',str(O/'bridge-i386.o')])
 assert not run('undefined',['nm','-u',str(O/'bridge-i386.o')]).strip()
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],host=r['host'])))
