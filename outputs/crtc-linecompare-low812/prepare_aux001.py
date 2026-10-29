"""Copy source-only auxiliary validators, preserving numeric offsets."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-cold810'
names=['layout_model.py','frontend_model002.py','clock_model004.py','link_review.py','layout_link_review.py','main_link_review.py']
for n in names:
 s=(O/n).read_text(encoding='utf-8')
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 s=''.join(re.sub(r'^0x810(?=[0-9a-f]{0,2}$)','0x812',p) if i%2 else p.replace('810','812') for i,p in enumerate(parts))
 assert not (K/n).exists();(K/n).write_text(s,encoding='utf-8')
(K/'aux-lineage001.json').write_text(json.dumps({'source_only':True,'parent':'CLOSED810 sources; no runtime reuse',
 'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names}},indent=2)+'\n')
for name,body in [('.gitattributes','* -text\n'),('.gitignore','__pycache__/\n*.pyc\n*.xbe\n*.exe\n*.obj\n*.jpg\n*.png\nconnection.json\n')]:
 assert not (K/name).exists();(K/name).write_text(body,encoding='ascii')
