"""Copy proven controller/tests into a fresh namespace; no physical access."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'stack-stop540';rows={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['controller.py','supervise.py','host001.py','stage-host002.py','audit.py','decode_actual.py',
 'primary_decode.py','witness_decode.py','decode.py','receipts.py','legacy_refusal_decode.py','failure_marker.py','stack_host.py']:
 src=S/name;t=src.read_text(encoding='utf-8');dest='stage-host001.py' if name=='stage-host002.py' else name
 if name in ['controller.py','supervise.py','host001.py','stage-host002.py','audit.py','decode_actual.py']:
  t=t.replace('stack-stop540','pre-c-stop541').replace('xwn540','xwn541').replace('XWNBoot540','XWNBoot541')
  t=t.replace('audit540','audit541').replace('completed540','completed541')
  t=t.replace('entry-footprint539/after1.json','stack-stop540/after1.json')
  t=t.replace('stage-host002.json','stage-host001.json')
 if name=='controller.py':t=t.replace('post-stack halt','pre-C halt')
 if name=='stack_host.py':
  t=t.replace('address==0x26000f0 or','address==(0x26000f0 if name==\'a\' else 0x2600200) or')
  t=t.replace('u.emu_start(0x26000f0,','u.emu_start(0x26000f0 if name==\'a\' else 0x2600200,')
  t=t.replace('==[0xa5,1]','==[0xa5 if name==\'a\' else 0x5f,1]')
  t=t.replace('Exact stack stub through intentional CLI','Exact late marker stub through intentional CLI')
 p=K/dest;assert not p.exists();p.write_text(t,encoding='utf-8',newline='\n')
 rows[dest]=dict(source=str(src),source_sha256=sha(src),sha256=sha(p))
(K/'workflow-copy001.json').write_text(json.dumps(dict(files=rows,physical_access=False),indent=2)+'\n',encoding='utf-8',newline='\n')
