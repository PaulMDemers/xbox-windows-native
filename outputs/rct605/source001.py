"""Copy qualified604 sources with scoped path/command namespaces only."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct604';out=K/'source001.json';assert not out.exists()
names=['fixture.c','subject002.c','graphics002.h','dib_header.h','dib_control.h','dib_oracle.py','calls.h','host_calls.c','host_test001.py','host_dib.c','host_dib001.py','header_tests001.py','trace.c','runner002.c','build002.py','binary_review001.py','media001.py','prepare001.py','edition.json','vm.py','trace_oracle.py','oracle_tests001.py','cold002.py','actions002.py','login001.py','input_transport001.py','event_timestamps001.py']
pins={}
for n in names:
 p=old/n;pins[n]=hashlib.sha256(p.read_bytes()).hexdigest();s=p.read_text(encoding='utf-8')
 for a,b in [('xwn604','xwn605'),('XWN604','XWN605'),('rct604','rct605'),('subject604','subject605'),('trace604','trace605'),('run604','run605')]:s=s.replace(a,b)
 s=s.replace('choices=[604]','choices=[605]').replace("'604'","'605'")
 if n=='prepare001.py':s=s.replace('fresh604','fresh605')
 if n=='build002.py':s=s.replace('probe_dib604 @9\\n','probe_dib604 @9\\nprobe_phase605 @10\\n')
 if n=='binary_review001.py':s=s.replace("(b'probe_dib604',9)]","(b'probe_dib604',9),(b'probe_phase605',10)]")
 (K/n).write_text(s,encoding='utf-8',newline='\n')
out.write_text(json.dumps(dict(source_pins=pins,scope='Preserve604 reader and601 graphics core; add new605 phase control separately.'),indent=2)+'\n')
