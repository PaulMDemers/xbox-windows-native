"""Preserve frozen checker and distinguish WORDS markers from sampling phase."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent
source=K/'trace_oracle.py';target=K/'trace_oracle002.py'
assert not target.exists()
s=source.read_text()
old="ident,phase,address,n,*values=v;assert n==len(values) and n<=36 and ident in calls and (ident,phase) not in words\n   words[ident,phase]=(address,values)"
new="ident,word_phase,address,n,*values=v;assert n==len(values) and n<=36 and ident in calls and (ident,word_phase) not in words\n   words[ident,word_phase]=(address,values)"
assert s.count(old)==1
target.write_text(s.replace(old,new),encoding='utf-8',newline='\n')
for src,dst in [('review001.py','review002.py'),('oracle_tests001.py','oracle_tests002.py'),('phase_oracle_tests001.py','phase_oracle_tests002.py')]:
 p=K/dst;assert not p.exists()
 t=(K/src).read_text().replace('from trace_oracle import validate','from trace_oracle002 import validate')
 t=t.replace('review001.json','review002.json').replace('oracle-tests001.json','oracle-tests002.json')
 p.write_text(t,encoding='utf-8',newline='\n')
(K/'oracle-correction002.json').write_text(json.dumps(dict(
 source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 corrected_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
 reason='Code inspection found WORDS tuple overwrote sample phase. Rename local descriptor marker only; no expected outcomes changed.',
 runtime_changed=False,original_preserved=True),indent=2)+'\n')
