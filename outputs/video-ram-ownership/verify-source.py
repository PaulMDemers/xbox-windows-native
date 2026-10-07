"""Compare every compiled display source with the reviewed authored bytes."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
root=Path('/home/paul/xbox-windows-native/build/video-ram-ownership-001/source')
src=root/'win32ss/drivers/displays/framebuf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((k/'patch-review.json').read_text());build=json.loads((k/'build-report.json').read_text())
dest=k/'source-verification.json';assert not dest.exists()
for n,h in r['source_files'].items():assert sha(src/n)==h,n
assert subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()==build['source_tree']
for p in k.glob('*.py'):ast.parse(p.read_text())
d=dict(passed=True,source_tree=build['source_tree'],compiled_source_files=r['source_files'],
 build_sha256=sha(k/'build-report.json'),patch_sha256=sha(k/'0109-ram-ownership.patch'),
 source_path=str(src),verifier_sha256=sha(Path(__file__)))
dest.write_text(json.dumps(d,indent=2)+'\n');print('Compiled source identity PASS',build['source_tree'])
