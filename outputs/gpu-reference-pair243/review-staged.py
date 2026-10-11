"""Exact staged source/report scope and bytes; forbid private payloads."""
import hashlib,json,re,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'staged-review001.json';assert not dest.exists()
def git(*args):return subprocess.check_output(['git','-C',str(ws),*args])
names=git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0');allowed=['outputs/gpu-reference-pair242/','outputs/gpu-reference-pair243/']
assert all(n in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md'] or any(n.startswith(p) for p in allowed) for n in names)
assert not git('diff','--name-only').strip(),'Unstaged tracked changes'
process=subprocess.Popen(['git','-C',str(ws),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE);rows=[];blobs={}
for n in names:
 process.stdin.write((':'+n+'\n').encode());process.stdin.flush();h=process.stdout.readline().split();assert len(h)==3 and h[1]==b'blob';data=process.stdout.read(int(h[2]));assert process.stdout.read(1)==b'\n'
 actual=(ws/n).read_bytes();normalized=n in ['.gitattributes','outputs/engineering-notes/CONTINUATION.md'];assert data==(actual.replace(b'\r\n',b'\n') if normalized else actual),n
 assert b'\0' not in data and not data.startswith(b'MZ') and len(data)<5*1024*1024 and Path(n).suffix.lower() not in {'.exe','.dll','.sys','.bin','.qcow2','.iso','.img','.xbe','.zip','.raw'}
 rows.append(dict(path=n,bytes=len(data),staged_sha256=hashlib.sha256(data).hexdigest(),worktree_sha256=hashlib.sha256(actual).hexdigest(),git_lf_normalized=normalized));blobs[n]=data
process.stdin.close();process.stdout.close();assert process.wait()==0
assert blobs['outputs/engineering-notes/CONTINUATION.md'].endswith(git('show','HEAD:outputs/engineering-notes/CONTINUATION.md'))
subprocess.run(['git','-C',str(ws),'diff','--cached','--check'],check=True)
dest.write_text(json.dumps(dict(passed=True,parent_head=git('rev-parse','HEAD').decode().strip(),files=rows,old_git_continuation_tail_preserved=True,source_scope_only=True,physical_access=False),indent=2)+'\n',encoding='utf-8')
check=ws/'tools/check-repository.py';source=check.read_text(encoding='utf-8');start=source.index('for name in files:');end=source.index('print(json.dumps',start)
patterns=[rb'gh[pousr]_[A-Za-z0-9]{25,}',rb'-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----',rb'(?i)(?:productkey|product_key|hddkey|hdd_key)\s*[=:]\s*["\x27]?[A-Za-z0-9-]{12,}']
exec(compile(source[start:end],str(check),'exec'),dict(root=ws,files=[dest.relative_to(ws).as_posix()],patterns=patterns,re=re))
print('242/243 exact staged source/evidence review PASS',len(rows))
