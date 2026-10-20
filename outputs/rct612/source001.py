"""Fresh child after611 host-space stop; same qualified observer and game case."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct611'
out=K/'source001.json';assert not out.exists()
f=json.loads((S/'final001.json').read_text());assert f['closed'] and not f['passed']
assert json.loads((K.parent/'rct610/final001.json').read_text())['passed']
assert json.loads((S/'archive001.json').read_text())['completed']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=json.loads((S/'source001.json').read_text());sources={}
names=list(src['sources'])+['lifetime_inheritance001.py','game_lifetime_tests001.py','layout_review001.py']
for n in names:
 p=S/n;s=p.read_text(encoding='utf-8')
 for prefix in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE']:s=s.replace(prefix+'611',prefix+'612')
 s=s.replace('choices=[611]','choices=[612]').replace("'611'","'612'")
 if n in ['media_review001.py','copy_contract_tests001.py']:s=s.replace(',611)',',612)')
 if n in ['prepare001.py','vm.py']:s=s.replace('require_space(P,21)','require_space(P,22)')
 assert not (K/n).exists();(K/n).write_text(s,encoding='utf-8',newline='\n')
 sources[n]=dict(source=str(p),sha256=sha(p))
for n in ['save','reference']:assert sha(Path(src[n]['path']))==src[n]['sha256']
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
out.write_text(json.dumps(dict(passed=True,sources=sources,save=src['save'],reference=src['reference'],roi=src['roi'],roi_rgb_sha1=src['roi_rgb_sha1'],physical_access=False,game_instrumentation=True,qualified_observer=src['qualified_observer'],change='Namespace-only game and observer; fresh404 child,22GiB initial capacity admission after lossless archive recovery.'),indent=2)+'\n')
