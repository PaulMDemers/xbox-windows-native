"""Reconstruct the immutable host receipt from exact public text chunks. No runtime."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;m=json.loads((K/'model-public001.json').read_text());parts=[]
for p in m['parts']:
 b=(K/p['file']).read_bytes();assert len(b)==p['bytes'] and hashlib.sha256(b).hexdigest()==p['sha256'];parts.append(b)
b=b''.join(parts);assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
p=K/m['original_file']
if p.exists():assert p.read_bytes()==b
else:
 with p.open('xb') as f:f.write(b)
print('Exact model receipt verified/restored; no runtime executed')
