"""Fresh754 source-only correction; token-aware namespace and full clock logging."""
import re,json,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;O=K.parent/'crtc-blank-end753'
def namespace(s,old,new):
 s=re.sub(r'0x'+old+r'(?=[0-9a-f]*\b)','0x'+new,s)
 return re.sub(r'(?<![0-9])'+old+r'(?![0-9])',new,s)
names=['main.c','layout.c','layout.h','probe.c','probe.h','Makefile','build.py','model.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','audit_logic.py','prefix_schema.py','physical.py','audit_collection.py']
assert not (K/'main.c').exists()
for n in names:(K/n).write_text(namespace((O/n).read_text(),'753','754'),newline='\n')
p=K/'main.c';s=p.read_text();assert 'if(frequency!=3375300)' in s;s=s.replace('if(frequency!=3375300)','if(frequency!=3375000)')
a=r'append("  \"kernel_qpc_frequency\":%lu,\n", (unsigned long)frequency);'
b=r'append("  \"kernel_qpc_frequency\":%lu,\"kernel_qpc_frequency_high\":%lu,\n", (unsigned long)frequency, (unsigned long)(frequency>>32));'
assert a in s;s=s.replace(a,b);p.write_text(s,newline='\n')
(K/'lineage001.json').write_text(json.dumps({'source_only_reuse':True,'closed_runtime_reused':False,'files':{n:hashlib.sha256((O/n).read_bytes()).hexdigest() for n in names},'delta':'token-aware753->754, exact clock3375000 restored, high32 frequency logging; CR03 transaction unchanged'},indent=2)+'\n',newline='\n')
