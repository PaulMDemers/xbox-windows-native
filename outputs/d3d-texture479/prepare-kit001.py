"""Fresh PC479 after 477 malformed floppy; token-bounded namespace substitutions."""
import hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];prior=K.parent/'d3d-texture477'
names=('build001.py','binary-review001.py','prepare001.py','cold002.py','preflight001.py',
       'run001.py','login001.py','review001.py','independent001.py','module-review001.py',
       'actual-controls001.py','closeout001.py','runner.c','launch_gate.py')
for name in names:
    p=K/name;assert not p.exists()
    s=(prior/name).read_text(encoding='utf-8')
    if name!='launch_gate.py':s=re.sub(r'(?<![0-9])477(?![0-9])','479',s)
    if name=='prepare001.py':
        assert s.count('1477560')==2;s=s.replace('1477560','1474560')
        s=s.replace("(P/'probe.img').write_bytes(image)","from floppy_check import validate\nfloppy_review=validate(bytes(image),{Path(r['path']).name.upper():Path(r['path']).read_bytes() for r in build['rows']})\n(P/'probe.img').write_bytes(image)")
        s=s.replace("'scope':'New child", "'floppy_review':floppy_review,'scope':'New child")
    if name=='build001.py':
        s=s.replace("sample=Path('/home/paul/xbox-windows-native/texture479-build001')", "sample=Path('/home/paul/xbox-windows-native/texture477-build001')")
    if name=='run001.py':
        s=s.replace("'sendkey '+key}","'sendkey '+key+' 20'}").replace('time.sleep(.09)','time.sleep(.2)')
    if name=='preflight001.py':
        s=s.replace("assert sha(Path(prep['source']))==prep['source_sha256']", "assert sha(Path(prep['source']))==prep['source_sha256']\nfrom floppy_check import validate\nfb=json.loads((K/'build001.json').read_text())\nassert validate((Path(prep['path'])/'probe.img').read_bytes(),{Path(r['path']).name.upper():Path(r['path']).read_bytes() for r in fb['rows']})==prep['floppy_review']\nassert json.loads((K/'floppy-tests001.json').read_text())['passed']")
    p.write_text(s,encoding='utf-8',newline='\n')
for name in ('oracle-tests001.json','inherited-gate-tests001.json'):
    (K/name).write_bytes((prior/name).read_bytes())
# Unexecuted physical478 points to the eventual qualified new PC, sample unchanged.
for name in ('build001.py','package001.py'):
    p=K.parent/'d3d-texture478'/name;s=p.read_text(encoding='utf-8')
    s=re.sub(r'(?<![0-9])477(?![0-9])','479',s);p.write_text(s,encoding='utf-8',newline='\n')
with (W/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n/outputs/d3d-texture479/** -text whitespace=cr-at-eol\n')
