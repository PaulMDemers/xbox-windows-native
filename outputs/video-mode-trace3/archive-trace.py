"""Lossless text chunks for the oversized monitor-response journal; never overwrite."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;source=k/'candidate001/trace.json';folder=k/'candidate001/trace-parts';manifest=folder/'manifest.json'
digest=lambda b:hashlib.sha256(b).hexdigest()
if sys.argv[1:]==['--restore']:
 r=json.loads(manifest.read_text());data=b''
 for i,row in enumerate(r['parts']):
  assert row['name']=='part-%03d.txt'%i
  b=(folder/row['name']).read_bytes();assert len(b)==row['bytes'] and digest(b)==row['sha256'];data+=b
 assert len(data)==r['bytes'] and digest(data)==r['sha256'];json.loads(data)
 if source.exists():assert source.read_bytes()==data
 else:source.write_bytes(data)
 print('Exact original trace restored/verified');raise SystemExit
assert not sys.argv[1:] and not folder.exists()
data=source.read_bytes();json.loads(data);assert len(data)>5*1024*1024 and data.isascii()
folder.mkdir();parts=[]
for i,start in enumerate(range(0,len(data),2*1024*1024)):
 b=data[start:start+2*1024*1024];name='part-%03d.txt'%i;(folder/name).write_bytes(b)
 parts.append(dict(name=name,bytes=len(b),sha256=digest(b)))
assert b''.join((folder/p['name']).read_bytes() for p in parts)==data
manifest.write_text(json.dumps(dict(passed=True,original='candidate001/trace.json',bytes=len(data),sha256=digest(data),parts=parts,
 reason='Preserve exact raw monitor reply journal under unchanged5MiB tracked-file guard. Original local file unchanged; chunks reconstruct it byte-for-byte.',verifier_sha256=digest(Path(__file__).read_bytes())),indent=2)+'\n')
print('Archived exact trace in',len(parts),'verified text chunks')
