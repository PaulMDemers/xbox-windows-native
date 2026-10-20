"""Fresh actual-game retry after the original610 lifetime control passed."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct609';Q=K.parent/'rct610'
out=K/'source001.json';assert not out.exists()
assert json.loads((Q/'final001.json').read_text())['passed']
assert json.loads((S/'final001.json').read_text())['closed']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=json.loads((S/'source001.json').read_text());sources={}
names=list(src['sources'])+['copy_contract.py','copy_contract_tests001.py','close001.py']
for n in names:
 p=S/n;s=p.read_text(encoding='utf-8')
 for prefix in ['xwn','XWN','rct','run','RUN','verify','VERIFY','trace','TRACE']:
  s=s.replace(prefix+'609',prefix+'611')
 s=s.replace('choices=[609]','choices=[611]').replace("'609'","'611'")
 if n in ['media_review001.py','copy_contract_tests001.py']:s=s.replace(',609)',',611)')
 assert not (K/n).exists();(K/n).write_text(s,encoding='utf-8',newline='\n')
 sources[n]=dict(source=str(p),sha256=sha(p))
for n in ['trace_oracle.py','lifetime.h']:
 p=Q/n;(K/n).write_bytes(p.read_bytes());sources[n]=dict(source=str(p),sha256=sha(p))
p=K/'trace.c';old=p.read_text();qualified=(Q/'trace.c').read_text();mark='void WINAPI mainCRTStartup(void)'
tail=old[old.index(mark):]
needle='if((DWORD)e.u.Exception.ExceptionRecord.ExceptionAddress==bp[i].address)'
assert tail.count(needle)==1
tail=tail.replace(needle,'if(!bp[i].retired&&(DWORD)e.u.Exception.ExceptionRecord.ExceptionAddress==bp[i].address)')
p.write_text(qualified[:qualified.index(mark)]+tail,encoding='utf-8',newline='\n')
p=K/'source_review001.py';s=p.read_text().replace("'rct607'","'rct610'").replace('rct607/','rct610/')
s=s.replace('Exact607 observer','Exact610 observer')
needle="assert 'count>10000'"
s=s.replace(needle,"assert (K/'lifetime.h').read_bytes()==(K.parent/'rct610/lifetime.h').read_bytes()\n"+needle)
p.write_text(s,encoding='utf-8',newline='\n')
p=K/'close001.py';s=p.read_text().replace('event-timestamps001.json','event-timestamps002.json');p.write_text(s,encoding='utf-8',newline='\n')
# Raw event decoder611 inherits609's corrected chronology text, not the older assertion.
p=S/'event_timestamps002.py';(K/p.name).write_text(p.read_text().replace('xwn609','xwn611'),encoding='utf-8',newline='\n')
sources[p.name]=dict(source=str(p),sha256=sha(p))
for n in ['save','reference']:assert sha(Path(src[n]['path']))==src[n]['sha256']
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
out.write_text(json.dumps(dict(passed=True,sources=sources,save=src['save'],reference=src['reference'],
 roi=src['roi'],roi_rgb_sha1=src['roi_rgb_sha1'],physical_access=False,game_instrumentation=True,
 qualified_observer=dict(path=str(Q/'trace.c'),sha256=sha(Q/'trace.c')),
 change='610 module generation, quiescent return-site retirement and fresh address reuse;609 retail inputs and cleanup retained.'),indent=2)+'\n')
