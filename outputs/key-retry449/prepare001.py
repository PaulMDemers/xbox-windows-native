"""New physical attempt namespace; preserve the consumed448 attempt unchanged."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent; old=K.parent/'key-xbox448'
out=K/'source-review001.json'; assert not out.exists()
rows=[]
for name in ['runner.c','build001.py','binary-review001.py','package001.py','physical.py','observe002.py','review001.py','actual-controls001.py','closeout001.py']:
    p=K/name; assert not p.exists()
    original=(old/name).read_bytes()
    updated=original.replace(b'key-xbox448',b'key-retry449').replace(b'448',b'449')
    p.write_bytes(updated)
    assert updated.replace(b'key-retry449',b'key-xbox448').replace(b'449',b'448')==original
    if name.endswith('.py'): compile(updated,str(p),'exec')
    rows.append(dict(file=name,original_sha256=hashlib.sha256(original).hexdigest(),new_sha256=hashlib.sha256(updated).hexdigest()))
out.write_text(json.dumps(dict(passed=True,changes='Namespace and schema448 to449 only; no sample, driver, mode or controller behavior change',rows=rows),indent=2)+'\n',encoding='utf-8')
print('Fresh449 sources prepared; exact448 reconstruction verified.')
