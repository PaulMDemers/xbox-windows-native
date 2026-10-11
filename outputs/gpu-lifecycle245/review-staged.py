"""Check exact staged bytes/scope and inherited continuation before private push."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'staged-review001.json';assert not dest.exists()
names=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0')
rows=[]
for name in names:
 assert name in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md'] or name.startswith(('outputs/gpu-lifecycle244/','outputs/gpu-lifecycle245/')),name
 data=(ws/name).read_bytes();staged=subprocess.check_output(['git','show',':'+name],cwd=ws)
 if name in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md']:assert data.replace(b'\r\n',b'\n')==staged
 else:assert data==staged,name
 assert len(staged)<5*1024**2 and b'\0' not in staged
 assert (ws/name).suffix.lower() not in ['.exe','.dll','.sys','.xbe','.bin','.qcow2','.img','.iso','.zip','.pcap']
 rows.append(dict(path=name,bytes=len(staged),staged_sha256=hashlib.sha256(staged).hexdigest()))
old=subprocess.check_output(['git','show','HEAD:outputs/engineering-notes/CONTINUATION.md'],cwd=ws)
now=subprocess.check_output(['git','show',':outputs/engineering-notes/CONTINUATION.md'],cwd=ws);assert now.endswith(old)
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,files=rows,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),old_continuation_tail_preserved=True,scope_limited=True,physical_access=False),indent=2)+'\n')
print('245 exact staged-source/report scope and inherited continuation PASS',len(rows))
