import hashlib,json,subprocess
from pathlib import Path
from integrate import transform
K=Path(__file__).resolve().parent
dest=K/'source-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
b=read(K/'build001.json');h=read(K/'host001.json')
assert b['status']=='compiled' and h['status']=='passed'
src='/home/paul/xbox-windows-native/build/stretch-bounds369-build001/source'
base='win32ss/drivers/displays/framebuf/'
def git(*args):return subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C',src,*args])
original=git('show',b['parent_tree']+':'+base+'shadow.c')
actual=git('show',b['source_tree']+':'+base+'shadow.c')
assert actual.decode()==transform(original.decode())
assert sha(original)==h['source_sha256']
for n in ['integrate.py','stretch_bounds.h']:assert sha((K/n).read_bytes())==h['inputs'][n]
changed=git('diff','--name-only',b['parent_tree'],b['source_tree']).decode().splitlines()
assert set(changed)=={base+n for n in ['shadow.c','stretch_bounds.h','CMakeLists.txt']}
assert not git('diff','--name-only')
for marker,nextmarker in [('static VOID XwnUploadBox','ULONG XwnCheckScanout'),('BOOL APIENTRY XwnPlgBlt','BOOL APIENTRY XwnAlphaBlend')]:
    def part(s):return s[s.index(marker):s.index(nextmarker,s.index(marker))]
    assert part(original.decode())==part(actual.decode())
actualhost=(Path('E:/xwn369/host001/actual.inc')).read_bytes()
s=actual.decode();extracted=s[s.index('static BOOL XwnRopUsesSource'):s.index('ULONG XwnCheckScanout')]+s[s.index('BOOL APIENTRY XwnStretchBlt('):s.index('BOOL APIENTRY XwnPlgBlt(')]
assert actualhost==extracted.encode() and sha(actualhost)==h['inputs']['actual.inc']
for n,pin in b['source_files'].items():assert sha(git('show',b['source_tree']+':'+n))==pin
r=dict(passed=True,parent_tree=b['parent_tree'],source_tree=b['source_tree'],changed=changed,
    matched_actual_host_wrappers=True,original_upload_enumerator_rows_unchanged=True,
    mapping_lifetime_and_other_wrappers_unchanged=True,host_inputs=h['inputs'],
    source_files=b['source_files'],physical_access=False,guest_launch=False,
    limits='Compiled candidate plus ASan/UBSan modeled-GDI host coverage; no actual Windows dispatch or speedup result.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Exact source closure and host/native wrapper identity passed')
