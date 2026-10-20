"""Fresh game retry after closing608's failed copy; preserve all failed bytes."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct608';out=K/'source001.json'
assert not out.exists()
f=json.loads((S/'final001.json').read_text());assert f['closed'] and not f['passed'] and f['cleanup_passed']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=json.loads((S/'source001.json').read_text());sources={}
for n in list(src['sources'])+['source_review001.py']:
 p=S/n;s=p.read_text(encoding='utf-8')
 for old in ['606','608']:
  for prefix in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE']:
   s=s.replace(prefix+old,prefix+'609')
  s=s.replace('choices=['+old+']','choices=[609]').replace("'"+old+"'","'609'")
 if n=='media_review001.py':
  s=s.replace("i.close()\n(K/'media-review001.json')","i.close()\nfrom copy_contract import validate\ncontract=validate(m['copy_script'],m['files'],json.loads((K/'build001.json').read_text())['rows'],609)\n(K/'media-review001.json')")
  s=s.replace('guest_copy_qualified=False','copy_contract=contract,guest_copy_qualified=False')
 (K/n).write_text(s,encoding='utf-8',newline='\n')
 sources[n]=dict(source=str(p),sha256=sha(p))
for n in ['save','reference']:assert sha(Path(src[n]['path']))==src[n]['sha256']
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
out.write_text(json.dumps(dict(passed=True,sources=sources,save=src['save'],reference=src['reference'],
 roi=src['roi'],roi_rgb_sha1=src['roi_rgb_sha1'],physical_access=False,game_instrumentation=True,
 change='Correct uppercase TRACE namespace; validate exact tool copy source/destination/execution against build and media.'),indent=2)+'\n')
print('609 sources prepared;608 failure preserved')
