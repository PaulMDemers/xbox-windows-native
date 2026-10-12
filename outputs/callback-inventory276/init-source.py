"""Fresh276 build harness only; no build or guest launch."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'owner-boundary274'
s=(old/'build-renderer.py').read_text().replace('patch274','patch276').replace('boundary274-build','callback276-build').replace('xemu-boundary274.exe','xemu-callback276.exe')
s=s.replace("('001','002')","('001',)").replace("prior=ws/'outputs/owned-lifetime273'","prior=ws/'outputs/owner-boundary274'").replace('renderer-source-pins001.json','renderer-source-pins002.json').replace('lifetime273-build001/source','boundary274-build002/source')
s=s.replace("inputs=['build-renderer.py','patch-renderer.py','boundary.h']","inputs=['build-renderer.py','patch-renderer.py','inventory.c']")
s=s.replace("{'hw/xbox/nv2a/pgraph/gl/texture.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h'}","{'hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h'}")
s=s.replace("print('274 bounded observation child", "print('276 read-only callback inventory")
for name,content in [('build-renderer.py',s),('BuildRenderer.ps1',(old/'BuildRenderer.ps1').read_text().replace("'001','002'","'001'").replace('274','276'))]:
    p=k/name;assert not p.exists();p.write_text(content)
