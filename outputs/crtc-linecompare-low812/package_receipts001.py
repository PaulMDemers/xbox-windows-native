"""Losslessly encode large host receipts for public retention; no runtime changes."""
from pathlib import Path
import hashlib,base64,zlib,json
K=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();m={'files':{}}
for name in ['model003.json','model005.json']:
 raw=(K/name).read_bytes();e={'original_sha256':sha(raw),'data':base64.b64encode(zlib.compress(raw,9)).decode('ascii')}
 out=K/(name+'.zlib64');assert not out.exists();out.write_text(json.dumps(e,separators=(',',':'))+'\n')
 assert zlib.decompress(base64.b64decode(e['data']))==raw
 m['files'][name]={'stored_as':out.name,'stored_sha256':sha(out.read_bytes()),'original_sha256':sha(raw),'original_bytes':len(raw)}
with (K/'receipt-storage001.json').open('x') as f:json.dump(m,f,indent=2);f.write('\n')
print('PASS exact host receipts encoded; originals retained')
