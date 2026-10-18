"""Fresh Xbox arithmetic characterization; 484/485 remain failed/held."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'d3d-blend485'
import json
sample=json.loads((K.parent/'blend-precision486/sample-build001.json').read_text())
sample_sha=sample['executable_sha256']
names=['build001.py','binary-review001.py','runner-build001.py','host001.py','test-wrapper.c','witness.S','decode.py','witness_decode.py','legacy_refusal_decode.py','failure_marker.py','transport001.py','controller-host001.py','physical.py','imports001.py','package001.py','review001.py','module-read001.py','actual-witness001.py','archive-inputs001.py','closeout001.py','process-closeout001.py']
for name in names:
    p=K/name;assert not p.exists()
    s=(old/name).read_text().replace('485','487')
    s=re.sub(r'(?<![0-9])484(?![0-9])','486',s)
    for a,b in [('d3d-blend486','blend-precision486'),('graphics_blend','graphics_precision'),('scoped_blend_passed','arithmetic_characterization_passed'),('blend_cases','arithmetic_cases'),('actual_blend_controls','actual_arithmetic_controls'),('r08cd','p486d'),('r08cs','p486s'),('edf7b7c796cd1ca1ba44a6c2cbbbab14007be003e7239cd2c92df65389927c12',sample_sha)]:s=s.replace(a,b)
    s=s.replace("W/'tools/graphics_precision.py'","W/'outputs/blend-precision486/graphics_precision.py'")
    s=s.replace("'tools/graphics_precision.py'","'outputs/blend-precision486/graphics_precision.py'").replace("'src/samples/graphics-ladder/blend.c'","'outputs/blend-precision486/precision.c'")
    if name in ['review001.py']:
        s=s.replace("sys.path.insert(0,str(W/'tools'));import graphics_precision as g","sys.path.insert(0,str(W/'tools'));sys.path.insert(0,str(K.parent/'blend-precision486'));import graphics_precision as g")
    if name=='physical.py':s=s.replace('len(listing)<=18','len(listing)<=22')
    if name=='controller-host001.py':s=s.replace('capacity18','capacity22').replace('capacity19','capacity23').replace('range(18)','range(22)').replace("==18 and","==22 and").replace('PASS 12 actual','PASS 12 actual')
    if name=='closeout001.py':
        s=s.replace('offscreen_software_rendering_qualified=True','offscreen_arithmetic_characterized=True,exact_ideal_alpha_qualified=False')
    p.write_text(s,encoding='utf-8',newline='\n')
p=K/'runner.c';assert not p.exists()
s=(K.parent/'blend-precision486/runner.c').read_text().replace('486','487').replace('Owned NT5 PC fixture only','Owned physical Xbox Windows fixture only')
# Keep the PC case names for byte-identical arguments while changing only fixture namespace.
s=s.replace('p487d','p486d').replace('p487s','p486s')
s=s.replace('A:'+chr(92)*2+'D3D.EXE','C:'+chr(92)*2+'xwn487-kit'+chr(92)*2+'d3d.exe')
p.write_text(s,encoding='utf-8',newline='\n')
p=K/'actual-controls001.py';assert not p.exists()
s=(K.parent/'blend-precision486/actual-controls001.py').read_text().replace("sys.path.insert(0,str(W/'tools'));import graphics_precision as g","sys.path.insert(0,str(W/'tools'));sys.path.insert(0,str(K.parent/'blend-precision486'));import graphics_precision as g")
s=s.replace("c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn486';rows=[]","c=json.loads((K/'physical001-collection.json').read_text());p=Path(c['files']['/E/xwn487/runner.txt']['path']).parent;rows=[]")
assert 'ntfs-cold' not in s;p.write_text(s,encoding='utf-8',newline='\n')
print('Fresh hardware arithmetic sources prepared; no deployment.')
