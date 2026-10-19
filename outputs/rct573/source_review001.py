"""MIT. Review exact successor scope and projected capacity before media."""
import ast,datetime,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct572'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'source-review001.json';assert not out.exists()
closed=json.loads((old/'final001.json').read_text());assert closed['closed']
for name,h in closed['pins'].items():assert sha(old/name)==h,name
assert (K/'runner.c').read_text().replace('573','572')==(old/'runner.c').read_text()
assert (K/'title_signature.h').read_text()==(old/'title_signature.h').read_text()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=(K/'input.h').read_text()
for token in ['KEYEVENTF_SCANCODE','KEYEVENTF_EXTENDEDKEY','MOUSEEVENTF_MOVE','gamewindowcount==1&&state(tag)','GetTickCount()-started<10000','reacquire("fullscreen_reacquire")','reacquire("window_reacquire")']:
    assert token in s,token
assert 'point(320-i*10,240-i*5)' not in s
build=json.loads((K/'runner-build001.json').read_text());assert build['status']=='compiled'
for name in ['runner.c','input.h','title_signature.h']:
    assert sha(K/name)==sha(Path('C:/xwn573/runner-build001')/name)
free=shutil.disk_usage('C:/').free;need=1600*1024**2;assert free-need>=20*1024**3
out.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),closed572_pins=len(closed['pins']),compiler_clean=True,parent_runner_namespace_only=True,title_reference_unchanged=True,projected_new_bytes=need,host_c_free=free,projected_remaining=free-need,wsl_backing_on_c=True,physical_access=False,limits='Static scope/build/storage checks; native input behavior remains unqualified.',pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and p.suffix in ['.c','.h','.py']}),indent=2)+'\n')
