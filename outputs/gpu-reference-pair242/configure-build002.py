"""Preserve unlaunched001 and failed strict harness; prepare unique corrected002."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
for name in ['build.py','Build.ps1']:
 p=k/('build002.py' if name=='build.py' else 'Build002.ps1');assert not p.exists()
 s=(k/name).read_text(encoding='utf-8').replace('build001','build002').replace('candidate001-source-pins','candidate002-source-pins')
 if name=='Build.ps1':s=s.replace('/build.py','/build002.py')
 p.write_text(s,encoding='utf-8')
for name in ['Run.ps1','test-consume.py','freeze.py']:
 p=k/name;s=p.read_text(encoding='utf-8').replace('build001','build002').replace('candidate001-source-pins','candidate002-source-pins');p.write_text(s,encoding='utf-8')
s=(k/'test-inventory.py').read_text(encoding='utf-8').replace('build001','build002').replace('test001','test002').replace("'-I'+str(out)","'-isystem',str(out)")
(k/'test-inventory002.py').write_text(s,encoding='utf-8')
(k/'build001-unlaunched.json').write_text(json.dumps(dict(guest_launch=False,compiled=True,host_review_passed=False,reason='Strict helper harness found signed comparisons;001 preserved before any launch. Header unused-parameter and duplicate harness container_of also preserved.',next='build002/test-inventory002'),indent=2)+'\n',encoding='utf-8')
