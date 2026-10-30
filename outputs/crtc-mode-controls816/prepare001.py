"""Fresh816 bit2-only CR1A diagnostic; CLOSED815 source-only reuse."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-mode-controls815'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert read(O/'closed001.json')['closed'] and read(O/'audit002.json')['passed']
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x815(?=[0-9a-f]{0,2}$)','0x816',p) if i%2 else p.replace('815','816') for i,p in enumerate(parts))
names=['main.c','probe.c','probe.h','layout.c','layout.h','Makefile','build.py','layout_model.py','frontend_model002.py','clock_model005.py','link_review.py','layout_link_review.py','main_link_review.py','prefix_audit.py','prefix_schema.py','physical.py','dashboard.py','controller_review002.py','audit_collection001.py','audit_logic.py','prefix002.py','tail002.py','.gitattributes','.gitignore']
for n in names:
 assert sha(O/n)==read(O/'sources001.json')[n]
 s=ns((O/n).read_text())
 if n=='probe.c':
  assert s.count('o->mc_target[0]=4;')==1
  s=s.replace('o->mc_target[0]=4;','o->mc_target[0]=o->mc_before[0]|4;')
  s=s.replace('Pinned704 final four geometry controls','Diagnostic alternative: CR1A bit2-only; remaining704 geometry controls')
 if n in ['prefix002.py','tail002.py','audit_logic.py']:
  s=s.replace('[4,16,131,224]','[60,16,131,224]').replace('62,64,4,16,131,224,4]','62,64,60,16,131,224,4]')
 assert not (K/n).exists();(K/n).write_bytes(s.encode())
(K/'lineage001.json').write_text(json.dumps(dict(parent={n:sha(O/n) for n in names},measurement=sha(O/'audit002.json'),source_only=True,delta='CR1A target raw04 -> own saved byte OR04 =3C; strict full-byte equality retained; namespace815->816',rationale_source='https://raw.githubusercontent.com/haiku/haiku/master/src/add-ons/accelerants/nvidia/engine/nv_crtc.c',scope='Kernel diagnostic, bit2-only alternative; not a functional Windows driver patch'),indent=2)+'\n')
print('Prepared816')
