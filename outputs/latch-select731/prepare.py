"""Fresh731 authored scaffold from729, never a closed runtime or binary."""
from pathlib import Path
import datetime,hashlib,json
K=Path(__file__).resolve().parent;S=K.parent/'kernel-samples729';P=Path('C:/xwn731')
assert not P.exists();P.mkdir()
files=['main.c','layout.c','layout.h','Makefile','build.py','layout_model.py','link_review.py','layout_link_review.py','main_link_review.py','physical.py']
lineage={}
for n in files:
 b=(S/n).read_bytes();lineage[n]=hashlib.sha256(b).hexdigest()
 t=b.decode().replace('\r\n','\n').replace('729','731')
 (K/n).write_text(t,newline='\n')
f=K/'main.c';t=f.read_text().replace('Kernel-context blank/gate/sequencer sampling731','Kernel-context CR22 observations under bounded GR04 selection731')
t=t.replace('words[125]','words[43]').replace('i<125','i<43').replace('write_control_armed','read_plane_control_armed').replace('write_control_returned','read_plane_control_returned')
t=t.replace('(result.code==0x7318 || result.code==0x7315)','(result.code==0x7313 || result.code==0x7315)')
f.write_text(t,newline='\n')
f=K/'Makefile';t=f.read_text().replace('CR1b','ReadPlanes');f.write_text(t,newline='\n')
f=K/'physical.py';t=f.read_text().replace('Kernel-context731 bounded blank/gate/sequencer sampling','Kernel-context731 CR22 observations under bounded GR04 selection')
t=t.replace('kernel-context minimal6302/oneCR1b05/saved6303 with32blank pairs and gate-beforeSEQ sample; full-byte final checks','kernel-context four GR04 read-plane selections, raw CR22 reads and exact GR04/selectors restoration; no CR22/CR33/timing writes')
t=t.replace('kernel-context bounded blank/gate/sequencer sampling','kernel-context bounded GR04 read-plane selection and CR22 reads')
f.write_text(t,newline='\n')
# Credentials stay private; active configuration only.
(P/'connection.json').write_bytes(Path('C:/xwn729/connection.json').read_bytes())
(K/'lineage001.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_files':lineage,'reuse':'Authored source only. No closed runtime/binary/fixture reused.'},indent=2)+'\n')
