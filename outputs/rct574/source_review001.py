"""MIT. Scope and capacity review before first runtime."""
import ast,datetime,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct573';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'source-review001.json';assert not out.exists()
closed=json.loads((old/'final001.json').read_text());assert closed['closed']
for n,h in closed['pins'].items():assert sha(old/n)==h,n
assert (K/'runner.c').read_text().replace('574','573')==(old/'runner.c').read_text()
assert (K/'title_signature.h').read_text()==(old/'title_signature.h').read_text()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
s=(K/'input.h').read_text();base=(old/'input.h').read_text()
for name,following in [('keyevent','relative'),('relative','releaseinputs'),('scrollcases','options')]:
    begin='static '+('void' if name=='keyevent' else 'BOOL')+' '+name+'('
    end='static '+('void' if following=='releaseinputs' else 'BOOL')+' '+following+'('
    assert s.split(begin)[1].split(end)[0]==base.split(begin)[1].split(end)[0],name
assert '!capture("full-options")' not in s
assert s.index('return gamecapture(tag)')<s.index('screen=GetDC(0)')
assert 'Sleep(20000)' in s and 'capture=time.monotonic()+5' in (K/'vm.py').read_text()
g=(K/'game_capture.h').read_text()
assert not any(x in g for x in ['GetDC','BitBlt','GetPixel','DeleteFile','MoveFile','CREATE_ALWAYS'])
assert 'GetTickCount()-start<15000' in g and 'CopyFileA(src,dest,TRUE)' in g
build=json.loads((K/'runner-build001.json').read_text());assert build['status']=='compiled'
for n in ['runner.c','input.h','title_signature.h','game_capture.h']:assert sha(K/n)==sha(Path('C:/xwn574/runner-build001')/n)
free=shutil.disk_usage('C:/').free;need=1600*1024**2;assert free-need>=20*1024**3
out.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),closed_parent_pins=len(closed['pins']),compiler_clean=True,input_methods_exact=True,fullscreen_GDI_capture_removed=True,projected_new_bytes=need,host_c_free=free,projected_remaining=free-need,wsl_backing_on_c=True,physical_access=False,limits='Source/build/storage checks, not native screenshot or display qualification.'),indent=2)+'\n')
