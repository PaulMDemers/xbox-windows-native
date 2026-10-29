"""Restore exact split evidence; never execute a runtime."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent
for manifest in K.glob('*-public001.json'):
 m=json.loads(manifest.read_text());parts=[]
 for p in m['parts']:
  b=(K/p['file']).read_bytes();assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'];parts.append(b)
 b=b''.join(parts);assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
 target=K/m['original_file']
 if target.exists():assert target.read_bytes()==b
 else:
  with target.open('xb') as f:f.write(b)
 print('Exact receipt verified/restored:',m['original_file'])
