"""Prepare one uniquely named observation build using exact267 sources."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'backend-actors267'
t=(p/'build-renderer.py').read_text().replace('exact265','exact267').replace('patch267','patch269').replace("prior=ws/'outputs/backend-ledger265'","prior=ws/'outputs/backend-actors267'").replace('renderer-source-pins003.json','renderer-source-pins001.json').replace('actors267-build','reuse269-build').replace('ledger265-build003/source','actors267-build001/source').replace('xemu-actors267.exe','xemu-reuse269.exe').replace('267 read-only','269 read-only')
t=t.replace("'hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/sdl.c']","'hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/sdl.c','hw/xbox/nv2a/pgraph/gl/texture.c']")
t=t.replace("inputs=['build-renderer.py','patch-renderer.py','actor-core.h','actors.c','context-extra.c']","inputs=['build-renderer.py','patch-renderer.py','watch.c']")
a=t.index(" assert set(r['changed_sources'])==");b=t.index('\n',a)
t=t[:a]+" assert set(r['changed_sources'])=={'hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/texture.c'}"+t[b:]
for n,data in [('build-renderer.py',t),('BuildRenderer.ps1',(p/'BuildRenderer.ps1').read_text().replace('Preserve267','Preserve269'))]:
    assert not (k/n).exists();(k/n).write_text(data)
print('269 build wrappers ready; no borrowed source modified')
