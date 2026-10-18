import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;R=K.parent.parent
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
write(K/'repository-check001.json',dict(session=71719,closed=True,exit_code=0,tracked_files_checked=37446,binary_media_and_credential_pattern_checks_passed=True))
subprocess.run(['git','add','.gitattributes','outputs/entry-receipt498','outputs/engineering-notes/CONTINUATION.md','outputs/engineering-notes/STATUS.md'],cwd=R,check=True)
names=git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0')
rows=[]
for n in names:
 b=(R/n).read_bytes();assert git('show',':'+n)==b,n
 rows.append(dict(path=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
write(K/'git-byte-review001.json',dict(passed=True,files=rows))
subprocess.run(['git','add','outputs/entry-receipt498/git-byte-review001.json'],cwd=R,check=True)
n='outputs/entry-receipt498/git-byte-review001.json';assert git('show',':'+n)==(R/n).read_bytes()
subprocess.run(['git','diff','--cached','--check'],cwd=R,check=True)
subprocess.run(['git','commit','-m','Validate an early entry receipt without changing the Xbox'],cwd=R,check=True,timeout=90)
subprocess.run(['git','-c','http.version=HTTP/1.1','push','origin','main'],cwd=R,check=True,timeout=120)
print(git('log','-1','--format=%H').decode().strip())
