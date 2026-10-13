"""Version the scan/boot controllers to consume exact resumed staging evidence."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['stock-scan341','stock-boot342']:
    d=K.parent/name;source=d/'physical.py';target=d/'physical002.py';assert not target.exists()
    s=source.read_text();old="    assert read(K.parent/'stock-stage340/physical001.json')['complete']"
    assert s.count(old)==1
    s=s.replace(old,"    sys.path.insert(0,str(K.parent/'stock-stage340'))\n    from completion002 import staged\n    staged()")
    assert s.count("read(K/'frozen.json')")==1
    s=s.replace("read(K/'frozen.json')","read(K/'frozen002.json')")
    target.write_text(s)
    frozen=json.loads((d/'frozen.json').read_text())
    for p in [target,K/'engine.py',K/'resume_engine.py',K/'resume002.py',K/'completion002.py',K/'prepare-consumers002.py',K/'physical001.json',K/'failure-inspection001.json']:
        frozen[p.relative_to(W).as_posix()]=sha(p)
    (d/'frozen002.json').write_text(json.dumps(frozen,indent=2)+'\n')
    print(name,'new controller; original frozen inputs retained')
