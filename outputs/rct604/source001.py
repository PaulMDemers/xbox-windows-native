"""Prepare new604 source namespaces; preserve601 arithmetic/ABI constants."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct601'
assert not (K/'source001.json').exists()
names=['fixture.c','subject002.c','graphics002.h','calls.h','host_calls.c','host_test001.py','trace.c','runner002.c','build002.py','binary_review001.py','media001.py','prepare001.py','edition.json','vm.py','trace_oracle.py','oracle_tests001.py']
pins={}
for n in names:
 p=old/n;pins[n]=hashlib.sha256(p.read_bytes()).hexdigest();s=p.read_text(encoding='utf-8')
 for a,b in [('xwn601','xwn604'),('XWN601','XWN604'),('rct601','rct604'),('subject601','subject604'),('trace601','trace604'),('run601','run604')]:s=s.replace(a,b)
 s=s.replace("choices=[601]","choices=[604]").replace("default=601)","default=600)")
 if n=='trace.c':s=s.replace('>60100','>60000')
 if n=='prepare001.py':s=s.replace('fresh601','fresh604')
 if n=='build002.py':s=s.replace('probe601 @7\\n','probe601 @7\\nprobe_dib604 @9\\n')
 if n=='binary_review001.py':s=s.replace("[(b'probe601',7)]","[(b'probe601',7),(b'probe_dib604',9)]")
 (K/n).write_text(s,encoding='utf-8',newline='\n')
for n in ['cold002.py','actions002.py','login001.py','input_transport001.py']:
 p=K.parent/'rct603'/n;pins['603/'+n]=hashlib.sha256(p.read_bytes()).hexdigest();s=p.read_text(encoding='utf-8')
 s=s.replace('xwn603','xwn604').replace('rct603','rct604').replace("'603'","'604'")
 (K/n).write_text(s,encoding='utf-8',newline='\n')
(K/'source001.json').write_text(json.dumps(dict(source_pins=pins,scope='Namespace-only transport copy; graphics additions are separate new604 sources. Core601 arithmetic, ABI and probe names retained.'),indent=2)+'\n')
