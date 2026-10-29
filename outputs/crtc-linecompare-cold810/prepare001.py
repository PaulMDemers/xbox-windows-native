"""Fresh cold-condition namespace; use CLOSED809 source only, never its runtime."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-bit809'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x809(?=[0-9a-f]{0,2}$)','0x810',p) if i%2 else p.replace('809','810') for i,p in enumerate(parts)).replace('crtc-linecompare-bit810','crtc-linecompare-cold810')
assert json.loads((O/'closed001.json').read_text())['closed']
names=['probe.c','probe.h','main.c','layout.c','layout.h','Makefile','build.py','model006.py','layout_model.py','clock_model004.py','frontend_model002.py','link_review.py','layout_link_review.py','main_link_review.py','controller_review003.py','physical.py','dashboard.py','audit_logic.py','prefix_schema.py','audit_collection002.py','restore_receipts001.py']
r=dict(source_only=True,physical_access=False,runtime_parent=False,parents={},outputs={})
for n in names:
 s=ns((O/n).read_text());r['parents'][n]=sha(O/n)
 if n=='physical.py':
  at="    verify();s=read(K/'stage001.json');assert s['completed']"
  assert s.count(at)==1
  s=s.replace(at,at+"\n    cold=read(K/'cold-ready001.json');assert cold['user_confirmed_ten_second_power_cycle'] and cold['dashboard_confirmed']")
 if n=='controller_review003.py':
  s=s.replace("r=dict(passed=True", "assert \"cold['user_confirmed_ten_second_power_cycle']\" in s and \"cold['dashboard_confirmed']\" in s\nr=dict(passed=True")
 assert not (K/n).exists();(K/n).write_bytes(s.encode());r['outputs'][n]=sha(K/n)
(K/'derivation001.json').write_text(json.dumps(r,indent=2)+'\n')
print('810 source only; explicit cold-reset evidence required before launch')
