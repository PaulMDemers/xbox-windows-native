"""Preserve frozen decoder's unsupported mask-form failure; new bounded decoder."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'decode-queue.py';q=k/'decode-queue002.py';assert not q.exists()
s=p.read_text();a="""    values=re.findall(r'^#\\s*define\\s+'+name+r'\\s+(0x[0-9A-Fa-f]+)\\b',text,re.M)
    assert len(values)==1,(name,values)
    return int(values[0],16)"""
b="""    values=re.findall(r'^#\\s*define\\s+'+name+r'\\s+([^\\r\\n]+)',text,re.M)
    assert len(values)==1,(name,values)
    raw=values[0].strip()
    if re.fullmatch(r'0x[0-9A-Fa-f]+',raw):return int(raw,16)
    m=re.fullmatch(r'\\(1\\s*<<\\s*(\\d+)\\)',raw)
    assert m and 0<=int(m[1])<32,(name,raw)
    return 1<<int(m[1])"""
assert s.count(a)==1;q.write_text(s.replace(a,b))
dest=k/'decode-failure001.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=False,stage='read-only post-trace decoder',source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),error='Actual PUSH0_ACCESS mask uses (1 << n), which frozen first decoder did not accept',recovery='New decoder002 accepts only exact hex or bounded single-bit shift literals; original frozen source unchanged',physical_access=False,guest_launch=False),indent=2)+'\n')
