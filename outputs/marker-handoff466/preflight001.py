"""Freeze source/dependency closure and reject malformed decoder outputs before launch."""
import ast,hashlib,json,struct,subprocess
from pathlib import Path
from decode import decode
from refusal_decode import decode_refusal
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'emu001';out=O/'preflight001.json'
assert not out.exists() and not (O/'runner-start.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
good=bad=0
for p in sorted(Path('C:/xwn466/host001').glob('case*.bin')):
 data=p.read_bytes()
 if len(data)==176:decode(data);good+=1
 else:
  try:decode(data)
  except ValueError:bad+=1
  else:raise AssertionError(p)
for p in sorted(Path('C:/xwn466/host001').glob('refusal*.bin')):
 data=p.read_bytes()
 if len(data)==96:decode_refusal(data);good+=1
 else:
  try:decode_refusal(data)
  except ValueError:bad+=1
  else:raise AssertionError(p)
sample=Path('C:/xwn466/host001/refusal55.bin').read_bytes();r=list(struct.unpack('<24I',sample))
for i,v in [(4,13),(5,0),(5,1),(5,8),(6,0x103),(8,0),(9,1),(11,0),(12,0),(13,0),(16,0x400)]:
 copy=r[:];copy[i]=v
 try:decode_refusal(struct.pack('<24I',*copy))
 except ValueError:bad+=1
 else:raise AssertionError(('mutation accepted',i))
for p in K.glob('*.py'):ast.parse(p.read_text())
# Pin the actual current dependency closure used by the inherited read-only tools.
old=json.loads((K.parent/'cromwell-devices414/emu001/frozen.json').read_text())
paths={W/p for p in old if (W/p).is_file()}
paths.update(K.glob('*.*'));paths.update((K.parent/'entry-marker465').glob('*.*'))
paths.update([K.parent/'release-readiness403/stock_io002.py',K.parent/'release-readiness403/analyze-allocation002.py'])
pins={p.relative_to(W).as_posix():sha(p) for p in sorted(paths) if p.is_file()}
external=[Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts')/n for n in ['with_xbox_resource.ps1','complete_xemu_instance.ps1','lib/xemu_instance.ps1','lib/test_storage.ps1','fatx_stage_boot.py']]
external.extend(Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib').glob('*.ps1'))
hostpins={str(p):sha(p) for p in external}
(O/'host-dependencies.json').write_text(json.dumps(hostpins,indent=2)+'\n')
(O/'frozen.json').write_text(json.dumps(pins,indent=2)+'\n')
out.write_text(json.dumps(dict(passed=True,decoder_accepts=good,decoder_rejections=bad,frozen_inputs=len(pins),external_dependencies=len(hostpins),physical_access=False),indent=2)+'\n')
