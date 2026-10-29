"""Restore exact diagnostic JSON receipts from public lossless text envelopes.
Existing receipts are verified and never overwritten. No fixture is executed.
"""
from pathlib import Path
import json,base64,zlib,hashlib
K=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
m=json.loads((K/'receipt-storage001.json').read_text())
for name,row in m['files'].items():
 data=(K/row['stored_as']).read_bytes();assert sha(data)==row['stored_sha256']
 envelope=json.loads(data);raw=zlib.decompress(base64.b64decode(envelope['data']))
 assert sha(raw)==row['original_sha256']==envelope['original_sha256'] and len(raw)==row['original_bytes']
 out=K/name;assert out.parent==K
 if out.exists():assert out.read_bytes()==raw
 else:
  with out.open('xb') as f:f.write(raw)
print('PASS all exact diagnostic receipts restored or verified; no runtime reopened')
