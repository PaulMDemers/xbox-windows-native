"""Reject real malformed477 and mutations of the corrected-size host copy."""
import hashlib,json
from pathlib import Path
from floppy_check import validate
K=Path(__file__).resolve().parent;old=K.parent/'d3d-texture477'
b=json.loads((old/'build001.json').read_text());wanted={Path(r['path']).name.upper():Path(r['path']).read_bytes() for r in b['rows']}
p=Path('/home/paul/xbox-windows-native/d3d-texture477-pc001/probe.img');raw=p.read_bytes()
out=K/'floppy-tests002.json';assert not out.exists();n=0
def refuse(data):
    global n
    try:validate(data,wanted)
    except ValueError:n+=1
    else:raise AssertionError('Malformed floppy accepted')
refuse(raw);fixed=raw[:1474560];assert not any(raw[1474560:]);r=validate(fixed,wanted)
for at in list(range(11,36))+[510,511,512,513,514,512+4608,19*512,19*512+11,19*512+26,19*512+28,33*512]:
    bad=bytearray(fixed);bad[at]^=1;refuse(bad)
refuse(fixed[:-1]);refuse(fixed+b'\0')
out.write_text(json.dumps(dict(passed=True,rejections=n,original_sha256=hashlib.sha256(raw).hexdigest(),
    original_bytes=len(raw),model_corrected_length_review=r,original_unchanged=p.read_bytes()==raw,
    scope='Host decoder validation only; no repaired disk used as runtime parent'),indent=2)+'\n')
print('Floppy decoder rejects:',n)
