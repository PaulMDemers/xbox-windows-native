"""Fresh sanitizer test of experimental bus/profile, not a physical controller."""
import datetime, hashlib, json, os, subprocess
from pathlib import Path
K=Path(__file__).resolve().parent
O=Path('/mnt/c/xwn698/host001')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'host001.json').exists()
import sys
sys.path.insert(0,str(K.parents[1]/'tools'))
from build_space import require_space
space=require_space(O,20.05)
O.mkdir(parents=True)
r={'passed':False,'physical_access':False,'scope':'exhaustive16-bit status/length checks and finite transaction ordering; host-only', 'space':space, 'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.[ch]')}}
try:
    cc=Path('/usr/bin/gcc-12').resolve()
    r['compiler_sha256']=hashlib.sha256(cc.read_bytes()).hexdigest()
    assert r['compiler_sha256']=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
    args=[str(cc),'-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(K/'xcal_bus.c'),str(K/'test_bus.c'),'-o',str(O/'test')]
    for name,cmd in [('compile',args),('run',[str(O/'test')])]:
        p=subprocess.run(cmd,capture_output=True,timeout=60)
        (O/(name+'.stdout')).write_bytes(p.stdout);(O/(name+'.stderr')).write_bytes(p.stderr)
        r[name]={'returncode':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()}
        assert p.returncode==0,(name,p.returncode)
    r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
    r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['run']['stdout'])
