"""Create the new build wrapper without consuming a build or modifying SDKs."""
from pathlib import Path
k=Path(__file__).resolve().parent
old=k.parent/'owned-lifetime273'
s=(old/'build-renderer.py').read_text().replace('273','274').replace('lifetime274','boundary274')
s=s.replace('outputs/unit-reuse269','outputs/owned-lifetime273').replace('renderer-source-pins005.json','renderer-source-pins001.json')
s=s.replace('reuse269-build005/source','lifetime273-build001/source')
s=s.replace("inputs=['build-renderer.py','patch-renderer.py','watch.c','lifetime.h','wire.h']", "inputs=['build-renderer.py','patch-renderer.py','boundary.h']")
s=s.replace("assert set(r['changed_sources'])=={'hw/xbox/nv2a/pgraph/gl/texture.c'}", "assert set(r['changed_sources'])=={'hw/xbox/nv2a/pgraph/gl/texture.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h'}")
for name,data in [('build-renderer.py',s),('BuildRenderer.ps1',(old/'BuildRenderer.ps1').read_text().replace('273','274'))]:
    p=k/name;assert not p.exists();p.write_text(data)
