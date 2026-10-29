"""Extend independent physical record schema; preserve prior byte checks."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;O=K.parent/'crtc-linecompare-cold810'
def ns(s):
 return re.sub(r'0x810(?=[0-9a-f]{0,2}\b)','0x812',s)
for n in ['prefix_schema.py']:
 assert not (K/n).exists();(K/n).write_text(ns((O/n).read_text()),encoding='utf-8')
s=ns((O/'audit_logic.py').read_text()).replace('790-word','820-word').replace('len(v)==790','len(v)==820').replace('v[766:]','v[766:790]')
s=s.replace('0x81246]','0x81246,0x81248]')
s=s.replace('(forward==0x812)','(forward in [0x812,0x81248])')
tail=''' cl18b,cl18t,cl18a,cl18f,cl18u,cl18m=v[790:796]
 cl18nb=[v[796+3*i] for i in range(8)];cl18nf=[v[797+3*i] for i in range(8)];cl18nu=[v[798+3*i] for i in range(8)]
 assert cl18a in [0,1] and 0<=cl18m<512
 if forward in [0x812,0x81248]:
  assert cl18a==int([cl18b]+cl18nb==[255,12,62,64,233,223,223,140,16])
  if cl18a:
   assert cl18t==255 and cl18t==(0x3ff&255)
   assert all(0<=n<=255 for n in [cl18f,cl18u]+cl18nf+cl18nu)
   assert cl18m==sum(1<<i for i,(a,b) in enumerate(zip([cl18u]+cl18nu,[cl18b]+cl18nb)) if a!=b)
   assert (cl18f==255 and cl18nf==cl18nb)==(forward==0x812)
  else:assert cl18t==cl18m==0 and cl18f==cl18u==0xffffffff and cl18nf==cl18nu==[0xffffffff]*8 and forward==0x81248
 else:assert v[790:796]==[0,0,0,0xffffffff,0xffffffff,0] and v[796:]==[0,0xffffffff,0xffffffff]*8
'''
needle=' assert c13attempt in [0,1]';assert s.count(needle)==1;s=s.replace(needle,tail+needle)
s=s.replace('and cl9m==0)','and cl9m==0 and cl18m==0)')
s=s.replace('else 0x81247 if cl9m','else 0x81249 if cl18m else 0x81247 if cl9m')
s=s.replace('or cl9m:assert','or cl9m or cl18m:assert')
s=s.replace(" return {'crtc_linecompare_bit':", " return {'crtc_linecompare_low':{'before':cl18b,'target':cl18t,'attempted':cl18a,'after':cl18f,'restored':cl18u,'cleanup_mask':cl18m,'neighbors_before':cl18nb,'neighbors_after':cl18nf,'neighbors_restored':cl18nu},'crtc_linecompare_bit':")
assert not (K/'audit_logic.py').exists();(K/'audit_logic.py').write_text(s,encoding='utf-8')
# New, uniquely named executions retain full compiled-result bytes for the independent schema.
s=(K/'model001.py').read_text().replace("out=K/'model001.json'","out=K/'model004.json'")
s=s.replace("'cr18':[v[790]", "'raw_result':v,'cr18':[v[790]")
(K/'model004.py').write_text(s,encoding='utf-8')
s=(K/'model003.py').read_text().replace("out=K/'model003.json'","out=K/'model005.json'")
s=s.replace("'raw_result':v,'writes'","'raw_result':v+extra,'writes'")
(K/'model005.py').write_text(s,encoding='utf-8')
