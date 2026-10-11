"""Create unique diagnostic build wrappers without touching borrowed sources."""
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'backend-ledger265'
t=(p/'build-renderer.py').read_text().replace('exact263','exact265').replace('patch265','patch267').replace('surface-pending263','backend-ledger265').replace("renderer-source-pins001.json'","renderer-source-pins003.json'").replace('ledger265-build','actors267-build').replace('pending263-build001/source','ledger265-build003/source').replace('xemu-ledger265.exe','xemu-actors267.exe').replace('265 read-only','267 read-only')
t=t.replace("'ui/xemu-thumbnail.cc']","'ui/xemu-thumbnail.cc','hw/xbox/nv2a/pgraph/gl/shaders.c','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/gloffscreen.h','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/sdl.c']")
t=t.replace("inputs=['build-renderer.py','patch-renderer.py','ledger-core.h','context.c','renderer.c','ui.c']","inputs=['build-renderer.py','patch-renderer.py','actor-core.h','actors.c','context-extra.c']")
t=t.replace("{'hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pfifo.c','hw/xbox/nv2a/nv2a.c','ui/xemu.c','ui/xui/main.cc','ui/xemu-thumbnail.cc'}","{'hw/xbox/nv2a/pgraph/gl/renderer.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pgraph/gl/shaders.c','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/gloffscreen.h','hw/xbox/nv2a/pgraph/thirdparty/gloffscreen/sdl.c','ui/xemu.c'}")
(k/'build-renderer.py').write_text(t)
(k/'BuildRenderer.ps1').write_text((p/'BuildRenderer.ps1').read_text().replace('Preserve265','Preserve267'))
t=(p/'host-tests.py').read_text().replace('ledger265-host001','actors267-host001').replace("['ledger-core.h','test-core.c']","['actor-core.h','test-actors.c']").replace("['host-tests.py','ledger-core.h','test-core.c']","['host-tests.py','actor-core.h','test-actors.c']").replace("base+'/test-core.c'","'-pthread',base+'/test-actors.c'")
(k/'host-tests.py').write_text(t)
print('267 build/host wrappers prepared; no borrowed sources changed')
