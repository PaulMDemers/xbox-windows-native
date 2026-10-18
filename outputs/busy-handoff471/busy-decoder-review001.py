"""New decoder negatives for busy-only status; old physical evidence is unchanged."""
import hashlib,json,struct
from pathlib import Path
from refusal_decode import decode_refusal
K=Path(__file__).resolve().parent;out=K/'busy-decoder-review001.json';assert not out.exists()
p=Path('C:/xwn471/host001/refusal61.bin');data=p.read_bytes();q=list(struct.unpack('<48I',data));assert q[25]==5
count=0
for status in (0,8,0x10,0x18,0x800,0x808,0x810,0x818):
 m=q[:];m[28]=status;m[36]=status
 try:decode_refusal(struct.pack('<48I',*m))
 except ValueError:count+=1
 else:raise AssertionError(('nonerror status accepted',status))
old=json.loads((K.parent/'physical-status469/collection001.json').read_text())['files']['/E/Applications/XWNBoot468a/refusal.bin'];p=Path(old['path']);b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==old['sha256']
try:decode_refusal(b)
except ValueError:count+=1
else:raise AssertionError('old namespace accepted')
out.write_text(json.dumps(dict(passed=True,new_negatives=count,old_physical_bytes_unchanged=True,no_runtime_requalification=True),indent=2)+'\n')
print(count)
