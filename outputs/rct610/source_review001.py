"""Review frozen build bytes and the unchanged call/graphics observation core."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct607';out=K/'source-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'build002.json').read_text());assert b['status']=='compiled'
for n,v in b['files'].items():
 p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256']
 if p.suffix in ['.c','.h'] and p.name!='target_iat.h':assert p.read_bytes()==(K/p.name).read_bytes()
for n in ['calls.h','dib_header.h','phase.h','host_calls.c','host_dib.c','host_phase.c','null_control.h']:
 assert (K/n).read_bytes()==(S/n).read_bytes(),n
a=(S/'trace.c').read_text();t=(K/'trace.c').read_text()
for x,y in [('xwn610','xwn607'),('XWN610','XWN607'),('subject610','subject607')]:t=t.replace(x,y)
start='static BOOL request(';end='void WINAPI mainCRTStartup'
assert t[t.index(start):t.index(end)]==a[a.index(start):a.index(end)]
unload=t[t.index('static BOOL unload601'):t.index('static BOOL addbp')]
assert all(s not in unload for s in ['readmem','bytewrite','VirtualProtect','WriteProcessMemory'])
assert unload.index('retire610(')<unload.index('bp[j].retired=TRUE')
assert t.count('!bp[i].retired&&bp[i].address==address')==1
assert t.count('!bp[i].retired&&(DWORD)e.u.Exception.ExceptionRecord.ExceptionAddress')==1
assert json.loads((K/'host-tests001.json').read_text())['passed']
out.write_text(json.dumps(dict(passed=True,parent_sha256=sha(S/'trace.c'),candidate_sha256=sha(K/'trace.c'),scope='Exact built source/header bytes; request/output/observe/stepping core unchanged. Unload admission precedes metadata retirement, with no departing-image memory access.'),indent=2)+'\n')
print('610 frozen source and lifetime boundary checks passed')
