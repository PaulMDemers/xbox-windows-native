"""Close host-only327 evidence without pretending a runtime was attempted."""
import ast,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
dest=k/'final-review.json';assert not dest.exists()
build=read(k/'build003.json');review=read(k/'build-review003.json');host=read(k/'host001.json');parser=read(k/'parser001.json')
assert build['compiled'] and not build['warnings'] and review['passed'] and host['passed'] and parser['passed']
assert sha(Path(build['output_windows']))==build['binary_sha256']==review['binary_sha256']
for n,h in build['source_pins'].items():assert sha(k/n)==sha(Path('E:/xwn327/build003')/n)==h
for n,h in host['inputs'].items():assert sha(k/n)==sha(Path('E:/xwn327/host001')/n)==h
for n,h in parser['inputs'].items():assert sha(k/n)==h
assert read(Path('E:/xwn327/host001/result.json'))==host
for n,p in review['providers'].items():assert sha(Path(p['path']))==p['sha256']
assert read(k/'source-review.json')['original_source_reconstructed_exactly']
original=(k.parent/'video-text-oracle206/gdi-probe.c').read_bytes();data=(k/'gdi-probe.c').read_bytes()
tree=ast.parse((k/'generate.py').read_text())
hooks=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='hooks' for t in n.targets))
newline=b'\r\n' if b'\r\n' in original else b'\n'
for old,new in reversed(hooks):
    new=new.replace(b'\n',newline);assert data.count(new)==1;data=data.replace(new,old)
assert data==original
assert (k/'text-cases.c').read_bytes()==(k.parent/'video-text-oracle206/text-cases.c').read_bytes()
correction=read(k/'source-review002.json');old=Path(correction['prior_source_preserved'])
assert sha(old)==correction['previous_sha256'] and sha(k/'large_cases.c')==correction['current_sha256']
for p in k.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
assert not Path('D:/').exists(),'Archive drive returned: verify inputs and continue runtime preparation instead of recording this blocker'
processes=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process xemu* -ErrorAction SilentlyContinue).Count'],capture_output=True,text=True,check=True)
assert int(processes.stdout.strip())==0
private={}
for folder in ['build002','build003','host001']:
    for p in (Path('E:/xwn327')/folder).rglob('*'):
        if p.is_file():private[str(p)]=dict(bytes=p.stat().st_size,sha256=sha(p))
r=dict(utc=datetime.now(timezone.utc).isoformat(),scope='host-only compiled probe/oracle/parser review',passed=True,
       native_build=True,pe_imports_verified=True,original206_source_reconstructed=True,
       host_compared_pixels=host['compared_pixels'],parser_negative_controls=parser['negative_controls'],
       guest_prepared=False,guest_launched=False,physical_access=False,performance_qualified=False,
       driver_changes=False,archive_drive_present=False,blocker='D: holds pinned322 emulator and never-executed317 preparation; user reconnect question pending',
       owned_sessions='closed',xemu_process_count=0,private_files=private,
       files={p.name:sha(p) for p in sorted(k.iterdir()) if p.is_file() and p.name!='final-review.json'})
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({key:r[key] for key in ['passed','host_compared_pixels','parser_negative_controls','guest_launched','archive_drive_present','xemu_process_count']}))
