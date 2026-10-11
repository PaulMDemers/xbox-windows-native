"""Compile exact242 compiled helper/slot, real QEMU atomic/LRU/queue headers."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;src=k/'artifacts/build004/source';out=k/'artifacts/inventory-test005';out.mkdir(exist_ok=False)
dest=k/'inventory-test005.json';assert not dest.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['atomic.h','compiler.h','queue.h','lru.h']:
 p=out/'qemu'/name;p.parent.mkdir(exist_ok=True);p.write_bytes((src/'include/qemu'/name).read_bytes())
p=src/'hw/xbox/nv2a/pgraph/gl/renderer.c';s=p.read_text(encoding='utf-8')
(out/'inventory-actual.inc').write_text(s[s.index('static bool inventory242_alive'):s.index('/* Caller owns actual FIFO lock;')],encoding='utf-8')
p=src/'hw/xbox/nv2a/nv2a_int.h';s=p.read_text(encoding='utf-8');start=s.index('typedef struct NV2AInventorySlot242');end=s.index('} NV2AInventorySlot242;',start)+len('} NV2AInventorySlot242;')
(out/'slot-actual.inc').write_text(s[start:end],encoding='utf-8')
(out/'test-inventory.c').write_bytes((k/'test-inventory.c').read_bytes())
r=dict(passed=False,source_sha256=sha(Path(__file__)),actual_inputs={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()},runs=[],scope='Exact compiled read-only inventory with model/clock/lock adapters and real QEMU LRU/queue/atomics; not GPU or callback completion proof',physical_access=False,guest_launch=False)
try:
 for level in ['0','2']:
  exe=out/('inventory-O'+level);argv=['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-O'+level,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-isystem',str(out),str(out/'test-inventory.c'),'-o',str(exe)]
  build=subprocess.run(argv,capture_output=True,text=True,timeout=120);assert build.returncode==0,build.stderr
  result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=120);r['runs'].append(dict(command=argv,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,executable_sha256=sha(exe)));assert result.returncode==0 and not result.stderr
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('242 actual bounded inventory O0/O2 ASan/UBSan PASS')
