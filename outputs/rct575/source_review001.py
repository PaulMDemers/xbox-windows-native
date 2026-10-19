"""MIT. Exact change scope and projected reserve before native execution."""
import ast,datetime,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct574'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
closed=json.loads((old/'final001.json').read_text());assert closed['closed']
for n,h in closed['pins'].items():assert sha(old/n)==h,n
for n in ['runner.c','input.h','title_signature.h']:
    assert (K/n).read_text().replace('575','574')==(old/n).read_text(),n
g=(K/'game_capture.h').read_text().replace('575','574')
changed=' if(ok){number("screenshot_settle_begin",GetTickCount());Sleep(10000);number("screenshot_settle_end",GetTickCount());ok=state("screenshot_done");}'
assert g.count(changed)==1
assert g.replace(changed,' if(ok)ok=state("screenshot_done");')==(old/'game_capture.h').read_text()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
build=json.loads((K/'runner-build001.json').read_text());assert build['status']=='compiled'
for n in ['runner.c','input.h','title_signature.h','game_capture.h']:assert sha(K/n)==sha(Path('C:/xwn575/runner-build001')/n)
free=shutil.disk_usage('C:/').free;need=1600*1024**2;assert free-need>=20*1024**3
out=K/'source-review001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),closed_parent_pins=len(closed['pins']),compiler_clean=True,input_methods_exact=True,only_game_capture_change='10000ms post-copy settling',projected_new_bytes=need,host_c_free=free,projected_remaining=free-need,wsl_backing_on_c=True,physical_access=False),indent=2)+'\n')
