"""Create new measurement-only351 from immutable348 sources; no old edits."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'primary-copy348'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (K/'build.py').exists()
for n in ['primary_copy.c','primary_plan.h']:(K/n).write_bytes((P/n).read_bytes())
s=(P/'build.py').read_text().replace('primary-copy348','eligible-copy351').replace('xwn348','xwn351')
s=s.replace("K.parent/'hd-profile345/build001.json'","K.parent/'primary-copy348/build001.json'").replace('e48e031228a0d6d483c7ac8273c40a34b75644e7','f9adc6373a147add130c8e619bd88ff726d80738').replace('build/hd-profile345-build001/source','build/primary-copy348-build001/source')
s=s.replace("['build.py','integrate.py','primary_copy.c','primary_plan.h','host001.json']","['build.py','integrate.py','eligible.h','primary_copy.c','primary_plan.h','host001.json']")
(K/'build.py').write_text(s)
s=(P/'Build.ps1').read_text().replace('primary-copy348','eligible-copy351');(K/'Build.ps1').write_text(s)
s=(P/'review.py').read_text().replace('xwn348','xwn351').replace("K/'host002.json'","K/'host001.json'").replace("'_XwnPrimarySnapshot',","'_XwnPrimarySnapshot','_XwnEligibleSnapshot',")
(K/'review.py').write_text(s)
q=K/'probe';q.mkdir()
for n in ['gdi-probe.c','text-cases.c','large_oracle.h','review-build.py']:(q/n).write_bytes((P/'probe'/n).read_bytes())
s=(P/'probe/large_cases.c').read_text().replace('0x58574438','0x58574439').replace('data[1]!=348','data[1]!=351').replace('PRIMARY348_','PRIMARY351_').replace('||data[11])','||data[11]||data[14])').replace('for(i=12;i<32;i++)','for(i=15;i<32;i++)')
assert s!=(P/'probe/large_cases.c').read_text();(q/'large_cases.c').write_text(s)
(q/'build.py').write_text((P/'probe/build.py').read_text().replace('xwn348','xwn351'))
for p in K.rglob('*.py'):ast.parse(p.read_text())
(K/'parent-inputs.json').write_text(json.dumps({str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file() and p.suffix in ['.py','.c','.h','.ps1']},indent=2)+'\n')
