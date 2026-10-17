"""Construct a new two-case NT5 control; no preparation or launch here."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'sprites-depth450'
def replace(s,a,b):
 assert a in s,a
 return s.replace(a,b)
rows={}
for name in ['prepare001.py','cold002.py','cold003.py','login001.py','run001.py','preflight001.py','independent001.py','launch_gate.py','binary-review001.py']:
 s=(old/name).read_text(encoding='utf-8')
 if name!='launch_gate.py':s=s.replace('sprites-depth450','lifecycle453').replace('450','453')
 if name=='preflight001.py':
  s=s.replace('graphics_sprites','graphics_lifecycle').replace('sprites.c','lifecycle.c').replace('sprites.cmd','lifecycle.cmd')
  s=replace(s,",'mode-tests001.json'",'')
  s=replace(s,"assert json.loads((K/'mode-tests001.json').read_text())['passed'] is True", "assert manifest['winnt/system32/psapi.dll']['sha256']==json.loads((K/'modules001.json').read_text())['psapi_sha256']")
  s=replace(s,"K/'runner.c',W/'tools/graphics_lifecycle.py'", "K/'runner.c',K/'oracle-tests001.json',K/'modules001.json',W/'tools/graphics_lifecycle.py'")
 if name=='independent001.py':
  s=replace(s,"'ddraw.dll','advapi32.dll'", "'ddraw.dll','advapi32.dll','psapi.dll'")
  s=replace(s,'20<len(selected)<60','12<len(selected)<30')
 if name=='run001.py':s=s.replace('temporary enumerated24-bit mode, restored before restart','unchanged desktop mode')
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8');rows[name]=hashlib.sha256(p.read_bytes()).hexdigest()
s=(K.parent/'sprites-xbox451/runner.c').read_text(encoding='utf-8').replace('Owned physical Xbox Windows fixture only','Owned NT5 PC fixture only').replace('451','453')
s=replace(s,'"default index8 r04di","hel index8 r04si","default rgb565 r04d6","hel rgb565 r04s6","default rgb32 r04d3","hel rgb32 r04s3"','"default r05d","hel r05s"')
s=replace(s,'"r04di","r04si","r04d6","r04s6","r04d3","r04s3"','"r05d","r05s"')
s=replace(s,'C:\\\\xwn453-kit\\\\sprites.exe','A:\\\\LIFE.EXE').replace('sprites.exe','life.exe').replace('i<6','i<2').replace('completed==6','completed==2')
p=K/'runner.c';assert not p.exists();p.write_text(s,encoding='utf-8');rows['runner.c']=hashlib.sha256(p.read_bytes()).hexdigest()
gate=json.loads((old/'inherited-gate-tests001.json').read_text());assert gate['gate_sha256']==rows['launch_gate.py']
(K/'inherited-gate-tests001.json').write_text(json.dumps(dict(gate,scope='Inherited exact gate tests; not rerun in453'),indent=2)+'\n')
(K/'kit-review001.json').write_text(json.dumps(dict(rows=rows,scope='Fresh two-case controller, unchanged-mode PC fixture, added PSAPI pin and lifecycle checker'),indent=2)+'\n')
