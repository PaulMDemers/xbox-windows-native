"""Confirm compiled test sources differ from611 only in owned namespace."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct611';out=K/'retry-inheritance001.json';assert not out.exists()
b=json.loads((K/'build001.json').read_text());rows=[]
for name,v in b['files'].items():
 p=Path(name.replace('/mnt/c/','C:/'))
 if p.suffix not in ['.c','.h']:continue
 old=(S/p.name).read_text(encoding='utf-8')
 for prefix in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE']:old=old.replace(prefix+'611',prefix+'612')
 assert old==(K/p.name).read_text(encoding='utf-8')
 assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'] and p.read_bytes()==(K/p.name).read_bytes()
 rows.append(p.name)
out.write_text(json.dumps(dict(passed=True,compiled_sources=rows,scope='Same test case and recorder as611, apart from unique owned namespace. Host admission alone increased; no guest guard waiver.'),indent=2)+'\n')
