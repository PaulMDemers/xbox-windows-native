"""Verify exactly staged bytes and tracked payload exclusions before commit."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'git-byte-review002.json';repo=K/'repository-check002.json';assert not out.exists() and not repo.exists()
names=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=W).decode().strip('\0').split('\0')
proc=subprocess.Popen(['git','cat-file','--batch'],cwd=W,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
rows=[]
try:
 for name in names:
  proc.stdin.write((':'+name+'\n').encode());proc.stdin.flush()
  header=proc.stdout.readline().decode().split();assert len(header)==3 and header[1]=='blob',header
  n=int(header[2]);data=proc.stdout.read(n);assert proc.stdout.read(1)==b'\n'
  assert data==(W/name).read_bytes(),name
  rows.append(dict(path=name,bytes=n,sha256=hashlib.sha256(data).hexdigest()))
 proc.stdin.close();assert proc.wait(timeout=10)==0
except BaseException:
 proc.kill();proc.wait();raise
subprocess.run(['git','diff','--cached','--check'],cwd=W,check=True,timeout=30)
out.write_text(json.dumps(dict(passed=True,files=len(rows),rows=rows),indent=2)+'\n')
r=subprocess.run([sys.executable,'-B',str(W/'tools/check-repository.py')],cwd=W,capture_output=True,text=True,timeout=600)
repo.write_text(json.dumps(dict(passed=r.returncode==0,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n')
assert r.returncode==0,r.stderr;print(r.stdout.strip());print('Exact staged bytes:',len(rows))
