"""Fresh reviewers and active controller; retain initial unadmitted CPU coverage."""
from pathlib import Path
import re,json
K=Path(__file__).resolve().parent;A=K.parent/'native-vblank-overflow804'
def ns(s):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x804(?=[0-9a-f]{0,2}$)','0x806',p) if i%2 else p.replace('804','806') for i,p in enumerate(parts)).replace('native-vblank-overflow806','native-vblank-low806')
s=(K/'cpu005.py').read_text().replace('cpu005','cpu006').replace('cpu-build005','cpu-build006').replace('cpu-run005','cpu-run006').replace('4096+0x1000:','4096+0xb00:').replace('[0x1000:0x67c0]','[0xb00:0x67c0]')
(K/'cpu006.py').write_bytes(s.encode())
(K/'build013.py').write_bytes((K/'build012.py').read_bytes().replace(b'cpu-run005',b'cpu-run006'))
s=(K/'physical008.py').read_text().replace('CR07 vertical-blank-start overflow bit3','CR15 vertical-blank-start low byte').replace('then CR07 36/3E/36, eight neighbors','then CR07 36/3E/36 and CR15 CF/DF/CF, eight neighbors').replace('own recovery before CR09 and CR12','own recovery before CR07, CR09 and CR12')
(K/'physical009.py').write_bytes(s.encode())
for n in ['controller_review001.py','publish_receipts001.py','restore_receipts001.py','dashboard_preflight001.py']:
 s=ns((A/n).read_text()).replace('physical008','physical009')
 if n=='dashboard_preflight001.py':s=s.replace('C:/xwn803/connection.json','C:/xwn805/connection.json')
 (K/n).write_bytes(s.encode())
(K/'.gitignore').write_bytes(b'model001.json\nmodel002.json\nintegration010.json\n')
(K/'qualification-note001.json').write_text(json.dumps({'cpu005':'Built only, never run; superseded before admission because payload-preservation assertion began at old0x1000 rather than new0xb00','active_cpu':'cpu006 checks full relocated payload; fresh fixtures required','active_build':'build013 uses cpu-run006','no_physical_launch':True},indent=2)+'\n')
print('806 active CPU coverage, controller and support reviewers prepared')
