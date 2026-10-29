"""Derive owned812 automatic-return controller from source-only809."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-bit809'
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x809(?=[0-9a-f]{0,2}$)','0x812',p) if i%2 else p.replace('809','812') for i,p in enumerate(parts))
names=['physical.py','controller_review003.py','audit_collection002.py','dashboard.py']
for name in names:
 s=ns((O/name).read_text())
 if name in ['physical.py','controller_review003.py']:s=s.replace('model006.json','model005.json')
 if name=='physical.py':
  s=s.replace('Kernel-context812 CR09 line-compare bit6 checkpoint','Kernel-context812 CR18 line-compare low byte checkpoint')
  s=s.replace("    verify();s=read(K/'stage001.json');assert s['completed']", "    assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,10,29,22,50,tzinfo=datetime.timezone.utc),'review-only cutoff'\n    verify();s=read(K/'stage001.json');assert s['completed']")
  s=re.sub(r"'purpose':'[^']*'", "'purpose':'Qualified kernel CR18 line-compare low-byte FF to FF after complete810 prefix; own saved-value CR18 recovery first, eight neighbors checked before output enable; same-value effectiveness unproved; automatic return after15 seconds; no native handoff or Windows'",s)
  s=re.sub(r"'observation':'[^']*'", "'observation':'Standing user authorization; fresh812 automatic-return CR18 FF to FF control after qualified prefix; one SITE only; no native handoff or Windows; no repeated boot'",s)
 if name=='audit_collection002.py':
  s=s.replace('crtc_linecompare_bit_control','crtc_linecompare_low_control').replace('len(v)==790','len(v)==820').replace('0x81246]','0x81246,0x81248]')
  # Require authenticated postlaunch dashboard, not merely prelaunch reachability.
  s=s.replace("assert observation['visual_result']=='not_observed' and read(K/'dashboard002.json')['reachable']", "assert observation['visual_result']=='not_observed'\n dashboard=read(K/'dashboard002.json');launch=read(K/'launch001.json')\n assert dashboard['authenticated'] and dashboard['reachable'] and launch['utc']<dashboard['utc']<=c['utc']")
 assert not (K/name).exists();(K/name).write_text(s,encoding='utf-8')
(K/'controller-lineage001.json').write_text(json.dumps({'source_only':True,'source_files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'closed_runtime_access':False},indent=2)+'\n')
