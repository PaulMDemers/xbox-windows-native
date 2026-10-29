"""Source-only derive collection/controller and independent native result schema."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent; A=K.parent/'native-linecompare-bit811'; B=K.parent/'crtc-linecompare-low812'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ns(s,old):
 parts=re.split(r'(0x[0-9a-fA-F]+)',s)
 return ''.join(re.sub(r'^0x'+old+r'(?=[0-9a-f]{0,2}$)','0x813',p) if i%2 else p.replace(old,'813') for i,p in enumerate(parts))
def put(n,s):
 with (K/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
for n in ['audit_logic.py','prefix_schema.py']:
 s=ns((B/n).read_text(),'812')
 if n=='prefix_schema.py':
  s=s.replace('assert v[8]==v[10] and not v[9]&0x200','assert v[8]==v[10]')
  s=s.replace('v[11]&0x80000001!=0x80000001 or v[13]&0x20','v[11]&0xe0000001!=0x40000001 or v[12]!=0 or v[9]&0x200 or v[13]&0x20')
  s=s.replace('v[11]&0x80000001==0x80000001 and not v[13]&0x20','v[11]&0xe0000001==0x40000001 and v[12]==0 and not v[9]&0x200 and not v[13]&0x20')
 put(n,s)
s=ns((A/'physical009.py').read_text(),'811')
s=s.replace("'crtc-linecompare-cold810'","'crtc-linecompare-low812'").replace("==790 and audit['raw_result'][0]==0x810","==820 and audit['raw_result'][0]==0x812")
s=s.replace('native CR09 line-compare bit6 control','native CR18 line-compare low-byte control')
s=s.replace("'purpose':'native preserving prefix", "'purpose':'CR18 FF/FF/FF own saved recovery and eight neighbors after native preserving prefix")
put('physical009.py',s)
s=ns((A/'dashboard_preflight001.py').read_text(),'811').replace('C:/xwn810/connection.json','C:/xwn812/connection.json')
put('dashboard_preflight001.py',s)
s=ns((A/'controller_review001.py').read_text(),'811').replace("==0x810","==0x812")
put('controller_review001.py',s)
put('control-derivation001.json',json.dumps({'source_only':True,'parent_files':{str(p.relative_to(K.parents[1])):sha(p) for p in [A/'physical009.py',A/'dashboard_preflight001.py',A/'controller_review001.py',B/'audit_logic.py',B/'prefix_schema.py']},'schema_CPU_delta':'Native CR0 mask, CR3 zero, IF clear; refuses incompatible context','no_console_access':True},indent=2)+'\n')
print('PASS source-only controller/schema derivation')
