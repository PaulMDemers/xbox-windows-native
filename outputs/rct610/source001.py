"""Fresh original lifetime control; preserve all closed runtimes and sources."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'rct607'
out=K/'source001.json';assert not out.exists()
names=['fixture.c','subject002.c','graphics002.h','dib_header.h','dib_control.h','calls.h','phase.h','phase_control.h','null_control.h','host_calls.c','host_dib.c','host_phase.c','trace.c','runner002.c','build002.py','binary_review001.py','media001.py','prepare001.py','cold002.py','vm.py','login001.py','actions002.py','input_transport001.py','edition.json','dib_oracle.py','trace_oracle.py','review001.py','oracle_tests001.py','phase_oracle_tests001.py','absent_tests001.py']
pins={}
for n in names:
 p=S/n;s=p.read_text(encoding='utf-8')
 for a,b in [('xwn607','xwn610'),('XWN607','XWN610'),('rct607','rct610'),('run607','run610'),('subject607','subject610'),('trace607','trace610'),('choices=[607]','choices=[610]'),("'607'","'610'")]:s=s.replace(a,b)
 assert not (K/n).exists();(K/n).write_text(s,encoding='utf-8',newline='\n')
 pins[n]=dict(source=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
(K/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
out.write_text(json.dumps(dict(passed=True,sources=pins,physical_access=False),indent=2)+'\n')
