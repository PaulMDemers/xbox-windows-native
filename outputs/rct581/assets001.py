"""Generate integrity metadata only, after exact SHA256 retail source checks."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
m=json.loads((K.parent/'rct577/disc-mapping001.json').read_text())
p=json.loads((K.parent/'rct565/package001.json').read_text())['files']
assert not (K/'assets.h').exists()
rows=[];proof={}
for name,v in sorted(p.items()):
 if not name.startswith('game/'):continue
 f=Path(v['path']);data=f.read_bytes();h=hashlib.sha256(data).hexdigest()
 assert h==v['sha256'] and len(data)==v['bytes'],name
 s=hashlib.sha1(data).digest();proof[name]=dict(bytes=len(data),sha256=h,sha1=s.hex())
 rows.append('{'+json.dumps(name.replace('/','\\'))+','+str(len(data))+',{' + ','.join(str(x) for x in s)+'}}')
assert len(rows)==502
(K/'assets.h').write_text('/* MIT. Hash metadata, no retail content. */\nstatic const struct {const char *path;DWORD size;BYTE sha1[20];} assets[]={\n'+',\n'.join(rows)+'\n};\n')
(K/'asset-integrity001.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Pinned',len(rows),'assets')
