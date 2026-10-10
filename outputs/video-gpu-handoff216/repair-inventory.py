"""Preserve prelaunch inventory failures, derive corrected NEW source captures."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'inventory001-failures.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for name,error in [('inventory-model.py','Inherited unique-offset cardinality remained22 instead of26; failed before header/report generation.'),('inventory-handoff.py','Historical launcher object is obj/LoadReactOS.o, not boot/LoadReactOS.o; failed before report generation.')]:
 p=k/name;rows.append(dict(source=name,sha256=sha(p),error=error,guest_launch=False,physical_access=False))
 q=k/name.replace('.py','002.py');assert not q.exists();t=p.read_text(encoding='utf-8')
 if name=='inventory-model.py':t=t.replace("k/'artifacts/model'","k/'artifacts/model002'").replace("for r in rows})==22","for r in rows})==26").replace('Reviewed214','Reviewed216')
 else:t=t.replace("k/'artifacts/handoff'","k/'artifacts/handoff002'").replace("/'boot/LoadReactOS.o'","/'obj/LoadReactOS.o'").replace('artifacts/handoff/launcher','artifacts/handoff002/launcher')
 q.write_text(t,encoding='utf-8')
dest.write_text(json.dumps(dict(preserved=True,failures=rows,partial_artifacts={p.relative_to(k).as_posix():sha(p) for root in ['artifacts/model','artifacts/handoff'] for p in sorted((k/root).rglob('*')) if p.is_file()}),indent=2)+'\n',encoding='utf-8')
