"""Prepare new checker/controller revisions; do not edit host-pinned sources."""
from pathlib import Path
import re,json,datetime
K=Path(__file__).resolve().parent
A=K.parent/'native-linecompare-low813';B=K.parent/'crtc-mode-controls816'
def put(n,s):
 with (K/n).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
for old,new in [('page_review008.py','page_review010.py'),('page_boundary009.py','page_boundary010.py')]:
 s=(K/old).read_text().replace('relptr=0x209000','relptr=0x20a000').replace('==0x208ec0','==0x209ec0').replace('32896','41088')
 s=s.replace('0x1ff9000','0x1ff7000')
 put(new,s)
put('prefix_schema.py',(A/'prefix_schema002.py').read_text().replace('813','817'))
for n in ['prefix_audit.py','audit_logic.py']:
 put(n,(B/n).read_text().replace('816','817'))
s=(A/'physical009.py').read_text().replace('813','817').replace('crtc-linecompare-low812','crtc-mode-controls816').replace('0x812','0x816').replace('==820','==917')
s=s.replace('Native817 CR09 line-compare bit6','Native817 preserving CR1A and remaining mode controls')
s=re.sub(r"'purpose':'.*?','xbe_sha256'", "'purpose':'Native four-control counterpart of kernel816; CR1A bit2 preserves other saved bits; full prefix and own-value recovery; 40KiB ten-page allocation; deliberate hold; no Windows or full visible mode replay','xbe_sha256'",s)
s=s.replace('native CR18 line-compare low-byte control','native preserving CR1A four-control sequence')
put('physical009.py',s)
put('controller_review001.py',(A/'controller_review001.py').read_text().replace('813','817').replace('0x812','0x816'))
put('invocation-failure001.json',json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'host checker invocation only','failure':'tail003 invoked with WSL Python against Windows Unicorn package; ImportError before output or test execution','correction':'Run tail003 using C:/Python314/python.exe; CPU fixtures use WSL Python','physical_access':False},indent=2)+'\n')
print('Prepared independent schema, bounded controller, disjoint COFF checker buffers')
