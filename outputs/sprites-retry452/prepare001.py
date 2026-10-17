"""Fresh retry namespace; preserve all consumed451 sources and results."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
old=K.parent/'sprites-xbox451'
out=K/'source-review001.json';assert not out.exists()
rows=[]
for name in ['runner.c','build001.py','binary-review001.py','package001.py','physical.py','observe002.py','review001.py','actual-controls001.py','closeout001.py']:
    src=(old/name).read_bytes()
    data=src.replace(b'sprites-xbox451',b'sprites-retry452').replace(b'451',b'452')
    assert data.replace(b'sprites-retry452',b'sprites-xbox451').replace(b'452',b'451')==src
    p=K/name;assert not p.exists();p.write_bytes(data)
    rows.append(dict(name=name,original_sha256=hashlib.sha256(src).hexdigest(),sha256=hashlib.sha256(data).hexdigest()))
out.write_text(json.dumps(dict(passed=True,changes='Only namespace/schema451 to452; original source reconstruction byte-exact',rows=rows),indent=2)+'\n',encoding='utf-8')
