"""Fresh host-only655 checks; no firmware, console, filesystem image or XBE."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/mnt/c/xwn655/host001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not (K/'host001.json').exists()
r=dict(status='preflight',physical_access=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save():(K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    sys.path.insert(0,str(W/'tools'));from build_space import require_space
    r['space']=require_space(B,minimum_gib=20.05)
    B.mkdir(parents=True);(B/'tmp').mkdir();env=dict(os.environ,TMPDIR=str(B/'tmp'),PYTHONDONTWRITEBYTECODE='1')
    cc=Path('/usr/bin/gcc-12').resolve()
    assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
    r['compiler_sha256']=sha(cc)
    inputs=list(K.glob('*.py'))+list(K.glob('*.c'))+list(K.glob('*.h'))+[K.parent/'receipt652/receipt.h']
    r['source_pins']={str(p.relative_to(W)):sha(p) for p in inputs}
    def run(name,args):
        r.setdefault('commands',[]).append([str(a) for a in args]);save()
        x=subprocess.run(args,capture_output=True,timeout=60,env=env)
        (B/(name+'.stdout')).write_bytes(x.stdout);(B/(name+'.stderr')).write_bytes(x.stderr)
        assert x.returncode==0,(name,x.returncode)
        return x
    flags=['-std=c99','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie']
    run('compile',[str(cc),*flags,str(K/'packet.c'),str(K/'test_packet.c'),'-o',str(B/'test-packet')])
    x=run('encoder',[str(B/'test-packet')]);r['encoder']=json.loads(x.stderr)
    r['receiver']=json.loads(run('receiver',[sys.executable,'-B',str(K/'test_receiver.py'),'--packets',str(B/'encoder.stdout'),'--output',str(B/'loopback001')]).stdout)
    run('compile-i386',[str(cc),'-m32','-std=c99','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-O2','-c',str(K/'packet.c'),'-o',str(B/'packet-i386.o')])
    assert run('undefined-i386',['nm','-u',str(B/'packet-i386.o')]).stdout==b''
    r['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()}
    r['status']='pass'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(status=r['status'],encoder=r.get('encoder'),receiver=r.get('receiver'))))
