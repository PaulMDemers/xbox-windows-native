"""Review scoped helper changes and verify sources actually consumed by build002."""
import difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'source-review002.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
src=read('source001.json');build=read('build002.json');assert build['status']=='compiled'
for name,v in src['sources'].items():assert sha(Path(v['source']))==v['sha256'],name
for name,v in build['files'].items():
 p=Path(name.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'],name
 if p.suffix in ['.c','.h']:assert p.read_bytes()==(K/p.name).read_bytes(),name
runner=(K/'runner002.c').read_text();header=(K/'input002.h').read_text();load=(K/'load_dialog002.h').read_text()
assert '"input002.h"' in runner and '"load_dialog002.h"' in header
assert 'FALSE,0,0,game,&si,&pi)' in runner and 'DEBUG_ONLY_THIS_PROCESS' not in runner
assert 'ReadProcessMemory' not in runner+header+load and 'WriteProcessMemory' not in runner+header+load
assert load.count('PostMessageA(loadbutton,BM_CLICK')==1
assert '#include "save_dialog.h"' not in header and 'save_owned_park' not in header
before=(K/'load_dialog.h').read_text();assert load==before.replace('if(f==INVALID_HANDLE_VALUE)return FALSE;size=','if(f==INVALID_HANDLE_VALUE)return FALSE;\n size=')
assert len(read('asset-integrity001.json'))==503
assert "r['event_id']==6006" in (K/'cold002.py').read_text()
diff=list(difflib.unified_diff(before.splitlines(),load.splitlines(),fromfile='load_dialog.h',tofile='load_dialog002.h'))
out.write_text(json.dumps(dict(passed=True,game_instrumentation=False,game_code_patch=False,debugger=False,one_load_submission=True,
 correction_diff=diff,save=src['save'],reference=src['reference'],frozen_build_sources=True,
 limits='Static source/build review; native UI behavior and saved pixels still require guest evidence.'),indent=2)+'\n')
print('603 frozen helper/source review passed; no debugger or game-memory hooks')
