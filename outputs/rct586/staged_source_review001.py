"""Verify index bytes equal the final frozen builds, preserving failed predecessors."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
for folder,build in [('rct585','build002.json'),('rct585/phase2-source','build002.json'),('rct586','build001.json')]:
    D=K.parent/folder;b=json.loads((D/build).read_text());assert b['status']=='compiled'
    for name,v in b['files'].items():
        p=Path(name.replace('/mnt/c/','C:/'))
        if p.suffix not in ['.c','.h']:continue
        source=D/p.name;rel=source.relative_to(W).as_posix()
        frozen=p.read_bytes();index=subprocess.check_output(['git','show',':'+rel],cwd=W)
        assert sha(frozen)==v['sha256'] and index==frozen==source.read_bytes(),rel
        rows.append(dict(path=rel,sha256=sha(index)))
out=K/'staged-source-review001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,rows=rows,failed_build001_preserved_separately=True,phase2_source_preparation_note='The initial preparation receipt predates the explicit reacquire check; the final frozen phase2 build and these exact staged bytes include it.'),indent=2)+'\n')
print('Exact staged/frozen source checks passed:',len(rows))
