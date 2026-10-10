"""Review exact staged225 bytes, closed lifecycle and repository rules without guest replay."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'repository-review.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
for n,h in read(k/'emulator-frozen.json').items():assert sha((ws/n).read_bytes())==h,n
h=read(k/'trace001/host-state.json');assert h['closed'] and h['cleanup_record_exists'] and all(h[n]==0 for n in ['observer_exit_code','runner_exit_code','tracer_exit_code','audit_exit_code'])
assert read(k/'evidence-review.json')['passed'] and read(k/'trace001/audit.json')['handoff_scope_passed']
offload=read(k.parent/'task-storage-offload/manifest-handoff225-20261010.json');assert len(offload['records'])==2 and all(v['status']=='complete' for v in offload['records'])
files=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ws).decode().strip('\0').split('\0');rows={}
for n in files:
 if n.startswith('outputs/video-loader-handoff225/') or 'handoff225' in n.lower():
  data=subprocess.check_output(['git','show',':'+n],cwd=ws);assert data==(ws/n).read_bytes(),n;rows[n]=sha(data)
syntax=[]
for p in k.rglob('*.py'):ast.parse(p.read_text(),filename=str(p));syntax.append(str(p.relative_to(k)))
subprocess.run(['git','diff','--cached','--check'],cwd=ws,check=True)
subprocess.run(['C:/Python314/python.exe','-B',str(ws/'tools/check-repository.py')],cwd=ws,check=True)
dest.write_text(json.dumps(dict(passed=True,checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__).read_bytes()),staged_byte_pins=rows,python_syntax=syntax,scope=__doc__+' Self/output excluded to avoid recursive pinning.',ordinary_full_qualification=False,gpu_ownership_qualified=False,physical_access=False),indent=2)+'\n');print('Exact staged225/offload byte pins',len(rows),'Python syntax',len(syntax))
