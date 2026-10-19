"""MIT. Mutate a host copy of the exact prepared FAT12 input; no guest launch."""
import hashlib,json
from pathlib import Path
from floppy_check import validate
K=Path(__file__).resolve().parent
b=json.loads((K/'build002.json').read_text());wanted={Path(r['path']).name.upper():Path(r['path']).read_bytes() for r in b['rows']}
prep=json.loads((K/'ntfs-preparation001.json').read_text());p=Path(prep['path'])/'probe.img';raw=p.read_bytes()
out=K/'floppy-tests002.json';assert not out.exists();n=0
assert hashlib.sha256(raw).hexdigest()==prep['floppy_sha256'];r=validate(raw,wanted)
for at in list(range(11,36))+[510,511,512,513,514,512+4608,19*512,19*512+11,19*512+26,19*512+28,33*512]:
 bad=bytearray(raw);bad[at]^=1
 try:validate(bad,wanted)
 except ValueError:n+=1
 else:raise AssertionError('Malformed floppy accepted')
for bad in [raw[:-1],raw+b'\0']:
 try:validate(bad,wanted)
 except ValueError:n+=1
 else:raise AssertionError('Wrong length accepted')
out.write_text(json.dumps(dict(passed=True,rejections=n,original_sha256=hashlib.sha256(raw).hexdigest(),review=r,original_unchanged=p.read_bytes()==raw),indent=2)+'\n')
print('Floppy controls passed:',n)
