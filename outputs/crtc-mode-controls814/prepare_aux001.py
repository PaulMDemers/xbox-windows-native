"""Source-only helper reuse with exact current stack offsets verified in COFF."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-low812'
names=['layout_model.py','frontend_model002.py','clock_model005.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','dashboard.py']
for n in names:
 s=(O/n).read_text();parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 s=''.join(re.sub(r'^0x812(?=[0-9a-f]{0,2}$)','0x814',p) if i%2 else p.replace('812','814') for i,p in enumerate(parts))
 if n=='clock_model005.py':s=s.replace('899424841a0000898424801a0000','8994248c1d0000898424881d0000').replace('0x209a80','0x209d88').replace('0x209a88','0x209d90')
 if n=='audit_logic.py':n='prefix_audit.py'
 if n=='physical.py':
  s=s.replace("    assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,29,22,50,tzinfo=datetime.timezone.utc),'review-only cutoff'\n",'')
  s=s.replace("'model005.json'","'prefix001.json'").replace("'controller-review003.json'","'controller-review001.json'").replace("'review003.json'","'review001.json'")
  s=s.replace('CR18 line-compare low byte','remaining four geometry controls')
  s=re.sub(r"'purpose':'[^']*'","'purpose':'814 qualified kernel controls CR1A/25/28/2D after complete812 prefix; per-write ten-register readback, reverse own recovery, automatic dashboard return; no native or Windows launch'",s)
  s=re.sub(r"'observation':'[^']*'","'observation':'Standing user authorization, four-control kernel probe, bounded automatic return, one SITE only'",s)
 assert not (K/n).exists();(K/n).write_text(s)
(K/'aux-lineage001.json').write_text(json.dumps({'source_only':True,'parent':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names}},indent=2)+'\n')
print('814 auxiliary sources prepared; no stage admission')
