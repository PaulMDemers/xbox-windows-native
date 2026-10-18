"""Namespace-only original decoders; context semantics are a separate extension."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'blend-precision487';rows=[]
for old,new in [('decode.py','primary_decode.py'),('witness_decode.py','witness_decode.py'),('legacy_refusal_decode.py','legacy_refusal_decode.py'),('failure_marker.py','failure_marker.py')]:
 p=K/new;assert not p.exists();source=(P/old).read_text();s=source.replace('487','490').replace('0x37383458','0x30393458').replace('0x37383452','0x30393452').replace('0x37383448','0x30393448')
 if old=='witness_decode.py':s=s.replace('from decode import decode','from primary_decode import decode')
 p.write_text(s);rows.append(dict(original=str(P/old),original_sha256=hashlib.sha256((P/old).read_bytes()).hexdigest(),output=new,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(K/'decoder-source001.json').write_text(json.dumps(dict(passed=True,namespace_only=True,rows=rows),indent=2)+'\n')
