import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
h=read(K/'host001.json');s=read(K/'supervisor-host002.json')
assert h['passed'] and h['case_count']==32 and s['passed'] and s['all_children_closed']
assert sha(K/'physical.py')==h['source_sha256'] and sha(K/'supervise002.py')==s['source_sha256']
for row,field in [(h,'private_files'),(s,'files'),(read(K/'supervisor-host001.json'),'files')]:
 for p,v in row[field].items():assert sha(Path(p))==v['sha256']
candidate=Path('C:/xwn499/build001/default.xbe');review=read(K.parent/'entry-launch499/review002.json')
assert review['passed'] and sha(candidate)==review['sha256']
deps=list(K.glob('*.py'))+[K/n for n in ['DESIGN.md','host001.json','supervisor-host002.json']]+[W/n for n in [
 'outputs/entry-receipt498/decode.py','outputs/entry-launch499/build001.json','outputs/entry-launch499/review002.json',
 'outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py',
 'tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json',
 'outputs/native-windows-physical-f/physical-cache-preflight.json']]+[Path(sys.executable),candidate]
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
r=dict(passed=True,candidate_sha256=sha(candidate),dependencies={str(p.resolve()):sha(p) for p in deps},
       controller_cases=32,supervisor_actual_children=3,physical_access=False,return_plan='NOT autonomous; needs new reviewed runner or entry-only return kit',
       private_files_rehashed=len(h['private_files'])+len(s['files'])+len(read(K/'supervisor-host001.json')['files']))
assert not (K/'package001.json').exists();(K/'package001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
print(json.dumps({k:v for k,v in r.items() if k!='dependencies'}))
