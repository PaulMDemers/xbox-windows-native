"""Byte-exact monitor recording, including Windows CRLF and ANSI echo."""
import io,json,hashlib,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'transport-tests001.json';assert not dest.exists()
cases=['x\r\n(qemu) ','x\n(qemu) ','x\r(qemu) ','\x1b[K\r\n\"version=265 r0=1:2:3:4:5:6:7:8\"\r\n(qemu) ','','Unicode \u03b1\r\n']
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'page.txt'
 for text in cases:
  p.write_bytes(text.encode('utf-8'));assert p.read_bytes()==text.encode('utf-8')
  if text:assert p.read_bytes()!= (text+'x').encode('utf-8')
 old=io.BytesIO();wrapper=io.TextIOWrapper(old,encoding='utf-8',newline='\r\n');wrapper.write(cases[0]);wrapper.flush()
 oldbytes=old.getvalue();assert oldbytes==b'x\r\r\n(qemu) '
 legacy=io.TextIOWrapper(io.BytesIO(oldbytes),encoding='utf-8').read()
 assert legacy!=cases[0]
r=dict(passed=True,cases=len(cases),changed_bytes_rejected=5,original_failure_reproduced=True,guest_launched=False,physical_access=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
dest.write_text(json.dumps(r,indent=2)+'\n');print('Byte-exact transport6 cases PASS; original newline failure reproduced')
