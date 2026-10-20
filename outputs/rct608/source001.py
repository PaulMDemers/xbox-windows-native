"""Fresh game retry only after the original absent-output control passes."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct606';Q=K.parent/'rct607';out=K/'source001.json';assert not out.exists()
assert json.loads((Q/'final001.json').read_text())['passed']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sources={}
names=['runner.c','input.h','load_dialog002.h','park_phase.h','park_reference.h','verify.c','assets.h','asset-integrity001.json','asset_header_check001.py','welcome.h','game_capture.h','title_signature.h','target_iat.h','calls.h','phase.h','dib_header.h','build001.py','binary_review001.py','imports_review001.py','media001.py','media_review001.py','prepare001.py','cold002.py','vm.py','login001.py','actions002.py','input_transport001.py','edition.json','scene_compare.py','scene_tests001.py','event_timestamps001.py','analyze_trace001.py','review001.py','oracle_tests001.py','process_review001.py']
for n in names+['trace.c','trace_oracle.py','dib_oracle.py']:
 parent=Q if n in ['trace_oracle.py','dib_oracle.py'] else S
 p=parent/n;s=p.read_text(encoding='utf-8')
 for old in ['606','607']:
  for prefix in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace']:
   s=s.replace(prefix+old,prefix+'608')
  s=s.replace('choices=['+old+']','choices=[608]').replace("'"+old+"'","'608'")
 if n=='trace.c':
  marker='void WINAPI mainCRTStartup(void)'
  s=(Q/'trace.c').read_text().split(marker)[0]+marker+s.split(marker,1)[1]
 (K/n).write_text(s,encoding='utf-8',newline='\n');sources[n]=dict(source=str(p),sha256=sha(p))
src=json.loads((S/'source001.json').read_text())
for n in ['save','reference']:assert sha(Path(src[n]['path']))==src[n]['sha256']
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
out.write_text(json.dumps(dict(passed=True,sources=sources,qualified_observer_sha256=sha(Q/'trace.c'),
 save=src['save'],reference=src['reference'],roi=src['roi'],roi_rgb_sha1=src['roi_rgb_sha1'],
 physical_access=False,game_instrumentation=True),indent=2)+'\n')
print('608 fresh game sources prepared after607 qualification')
