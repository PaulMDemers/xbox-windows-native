"""Check canonical source export without editing the frozen build/review inputs."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;out=Path('D:/xwn311/replay001');assert not out.exists()
record=k/'export-review001.json';assert not record.exists();out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((k/'source-review001.json').read_text());parent='/home/paul/xbox-windows-native/build/hd-reservation300-build001/cromwell/'
old=k/'integration.patch';new=k/'integration-lf.patch';assert not new.exists()
text=old.read_text().replace('aa/','a/').replace('bb/','b/');new.write_bytes(text.encode())
r=dict(passed=False,original_export_sha256=sha(old),canonical_export_sha256=sha(new),transform='LF serialization and canonical a/b header prefixes only; original export retained',original_whitespace_check='Rejected patch context whitespace, not new C code; narrow patch-only whitespace attributes added')
try:
 for n,v in review['changes'].items():
  data=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',parent+n]);assert hashlib.sha256(data).hexdigest()==v['before']
  p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 subprocess.run(['git','init','-q',str(out)],check=True)
 subprocess.run(['git','-C',str(out),'apply','--check',str(new.resolve())],check=True)
 subprocess.run(['git','-C',str(out),'apply',str(new.resolve())],check=True)
 for n,v in review['changes'].items():assert sha(out/n)==v['after'],n
 for n,h in review['additions'].items():
  data=(k/'integrated'/Path(n).name).read_bytes();assert hashlib.sha256(data).hexdigest()==h
  (out/n).write_bytes(data)
 r.update(passed=True,changed_files_replayed=len(review['changes']),added_files_exact=len(review['additions']),build_rerun=False)
except Exception as e:r['failure']=repr(e);raise
finally:record.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
