"""Losslessly retain our numeric diagnostic traces as bounded compressed text."""
from pathlib import Path
import json,hashlib,zlib,base64
K=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest={}
for name in ['tail001.json','prefix001.json','integration001.json']:
 p=K/name;data=p.read_bytes();obj=json.loads(data)
 assert obj['passed'] and isinstance(obj['cases'],list)
 assert all(isinstance(c['name'],str) and all(isinstance(n,int) for n in c['raw_result']) for c in obj['cases'])
 packed=base64.b64encode(zlib.compress(data,9)).decode('ascii')
 assert zlib.decompress(base64.b64decode(packed))==data
 dest=K/(p.stem+'-receipt001.json');assert not dest.exists()
 item={'format':'zlib-base64 diagnostic JSON; no executable data','original_file':name,'original_bytes':len(data),'original_sha256':sha(data),'host_validation_only':True,'case_count':len(obj['cases']),'data':packed}
 encoded=(json.dumps(item,indent=2)+'\n').encode();assert len(encoded)<5*1024*1024;dest.write_bytes(encoded)
 manifest[name]={'stored_as':dest.name,'stored_sha256':sha(encoded),'original_sha256':sha(data),'original_bytes':len(data),'exact_roundtrip':True}
out=K/'receipt-storage001.json';assert not out.exists();out.write_text(json.dumps({'passed':True,'files':manifest,'limits':'Actual instruction execution with modeled device behavior; not physical timing or hardware semantics'},indent=2)+'\n')
print('PASS exact compressed-text roundtrip of three complete diagnostic receipts')
