import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'source-review001.json';assert not dest.exists()
old=Path('/home/paul/xbox-windows-native/build/hd-profile345-build001/source');new=Path('/home/paul/xbox-windows-native/build/primary-copy348-build001/source');rel=Path('win32ss/drivers/displays/framebuf')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((K/'build001.json').read_text())
assert subprocess.check_output(['git','-C',str(new),'write-tree'],text=True).strip()==build['source_tree']
assert not subprocess.check_output(['git','-C',str(new),'diff','--name-only'])
changed=subprocess.check_output(['git','-C',str(new),'diff','--name-only',build['parent_tree'],build['source_tree']],text=True).splitlines()
allowed=['CMakeLists.txt','enable.c','framebuf.h','ownership.c','primary_copy.c','primary_plan.h','shadow.c']
assert sorted(changed)==sorted(str(rel/n) for n in allowed)
a=(old/rel/'shadow.c').read_text();b=(new/rel/'shadow.c').read_text()
start='static VOID XwnUploadBox(';end='BOOL APIENTRY XwnCopyBits('
assert a[a.index(start):a.index(end)]==b[b.index(start):b.index(end)]
start='BOOL APIENTRY XwnTextOut(';assert a[a.index(start):]==b[b.index(start):]
for n in ['surface.c','screen.c','pointer.c','row_store.h','profile_math.h','text_bounds.h','surface_bounds.h']:assert (old/rel/n).read_bytes()==(new/rel/n).read_bytes()
for n in ['primary_plan.h','primary_copy.c']:assert sha(new/rel/n)==sha(K/n)==json.loads((K/'host002.json').read_text())['inputs'][n]
move=list((old/'sdk/lib').rglob('memmove_asm.s'));assert len(move)==1
baseline=Path('/mnt/e/xwn345/build001/candidate001/xwnown.dll');assert sha(baseline)==json.loads((K.parent/'hd-profile345/build001.json').read_text())['cases']['candidate001']['sha256']
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-objdump';private=Path('/mnt/e/xwn348/source-review001');assert not private.exists();private.mkdir()
instructions={}
for symbol in ['_XwnUploadBox','_memmove']:
    p=private/(symbol+'.txt');p.write_bytes(subprocess.check_output([tool,'-d','--disassemble='+symbol,str(baseline)],stderr=subprocess.DEVNULL));instructions[symbol]=sha(p)
    if symbol=='_XwnUploadBox':assert 'call   15340 <_memmove>' in p.read_text()
    else:assert 'rep movsl' in p.read_text()
reports=['video-late-cache-review/REPORT.md','video-scalar-runtime209/REPORT.md','video-dib-copy182/REPORT.md','hd-phase-physical347/pair-results.json']
r=dict(passed=True,parent_tree=build['parent_tree'],source_tree=build['source_tree'],changed_paths=changed,unchanged_upload_and_other_ddis=True,unchanged_surface_mapping_lifetime=True,exact_host_tested_adapter=True,local_memmove_source={'path':str(move[0]),'sha256':sha(move[0])},compiled345_source_discriminator={'binary_sha256':sha(baseline),'private_instruction_hashes':instructions,'conclusion':'Local libcntpr memmove and aligned REP MOVSD; no imported copy provider.'},prior_evidence={n:sha(K.parent/n) for n in reports},limits='Source/compiled review only. Historical cache review does not establish a fresh1080 physical PTE/alias inventory. No mapping/cache change proposed or made.',runtime=False,physical_access=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('348 source closure and exact existing upload PASS')
