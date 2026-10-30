"""Fresh815 kernel control uses measured814 baseline; source-only reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-mode-controls814'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert read(O/'closed001.json')['closed'] and read(O/'audit002.json')['passed']
v=read(O/'audit002.json')['raw_result'];assert v[820:830]==[56,16,131,224,104,48,227,255,62,64] and v[834]==0

def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x814(?=[0-9a-f]{0,2}$)','0x815',p) if i%2 else p.replace('814','815') for i,p in enumerate(parts))
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','frontend_model002.py','clock_model005.py','link_review.py','layout_link_review.py','main_link_review.py','prefix_audit.py','prefix_schema.py','physical.py','dashboard.py','controller_review002.py','audit_collection001.py','audit_logic.py','prefix002.py','tail002.py','.gitattributes','.gitignore']
for n in names:
 assert sha(O/n)==read(O/'sources001.json')[n]
 s=ns((O/n).read_text())
 if n=='probe.c':
  assert s.count('mc_baseline[10]={0,0x10,0x83,0,')==1
  s=s.replace('mc_baseline[10]={0,0x10,0x83,0,','mc_baseline[10]={0x38,0x10,0x83,0xe0,')
  s=s.replace('Strict720p-derived baseline admission','Strict measured814 baseline admission')
 if n in ['prefix002.py','tail002.py','audit_logic.py']:
  s=s.replace('{0x1a:0,0x28:0x83,0x2d:0}','{0x1a:0x38,0x28:0x83,0x2d:0xe0}')
  s=s.replace('[0,16,131,0,104,48,227,255,62,64','[56,16,131,224,104,48,227,255,62,64')
  s=s.replace('[4,16,131,0]','[4,16,131,224]').replace('62,64,4,16,131,0,4]','62,64,4,16,131,224,4]')
 if n=='layout_model.py':s=s.rstrip()+'\n'
 assert not (K/n).exists();(K/n).write_bytes(s.encode())
(K/'lineage001.json').write_text(json.dumps(dict(parent={n:sha(O/n) for n in names},measurement=sha(O/'audit002.json'),source_only=True,delta='CR1A/CR2D baseline00/00 -> measured38/E0; targets and saved high-bit preservation unchanged; namespace814->815'),indent=2)+'\n')
print('Prepared815 measured baseline; no hardware access')
