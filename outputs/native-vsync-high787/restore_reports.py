"""Restore lossless public report parts locally; no runtime execution."""
from pathlib import Path
import json,hashlib
k=Path(__file__).resolve().parent
for m in k.glob('*.parts.json'):
 r=json.loads(m.read_text());data=b''
 for p in r['parts']:
  b=(k/p['name']).read_bytes();assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'];data+=b
 assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
 target=k/r['file']
 if target.exists():assert target.read_bytes()==data
 else:target.write_bytes(data)
 print('Verified',r['file'])
