"""Validate actual cold witness and reject malformed copies without editing it."""
import hashlib,json,struct
from pathlib import Path
from witness_decode import decode_witness,classify
K=Path(__file__).resolve().parent;out=K/'actual-witness001.json';assert not out.exists()
c=json.loads((K/'physical001-collection.json').read_text())
root='/E/Applications/XWNBoot483a/'
assert c['completed'] and c['hook_removed'] and c['files'][root+'refusal.bin'] is None
def get(name):
 row=c['files'][root+name];data=Path(row['path']).read_bytes()
 assert hashlib.sha256(data).hexdigest()==row['sha256'];return data
p=get('report.bin');w=get('handoff.bin');r=classify(p,w);assert r['boundary_observed'] and not r['boot_qualified']
n=0
def reject(data):
 global n
 try:decode_witness(data,p)
 except ValueError:n+=1;return
 raise AssertionError('malformed actual witness accepted')
for size in range(256):reject(w[:size])
reject(w+b'\0')
for word in list(range(16))+list(range(40,64)):
 for bit in range(32):
  b=bytearray(w);b[word*4+bit//8]^=1<<(bit%8);reject(b)
for word,value in [(16,0),(21,0),(22,1),(23,1),(24,8),(25,4097),(30,8),(31,8),(32,0),(33,0),(34,0),(35,0),(36,3),(37,0),(38,0),(39,1)]:
 b=bytearray(w);struct.pack_into('<I',b,word*4,value);reject(b)
assert get('report.bin')==p and get('handoff.bin')==w
out.write_text(json.dumps(dict(passed=True,actual_witness=r,negative_controls=n,originals_unchanged=True,source_note='cold physical files; mutation tests operate only on copies',historical_failure_explained=False),indent=2)+'\n')
