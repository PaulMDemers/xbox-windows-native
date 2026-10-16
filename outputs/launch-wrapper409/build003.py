"""Build an isolated pre-UI allocation recorder from the exact deployed wrapper."""
import datetime, hashlib, json, os, shutil, struct, subprocess, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/build/resolution-e374-build001/source')
O=Path('/mnt/e/xwn409/build003')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'build003.json').exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(O.parent)
assert shutil.disk_usage('/mnt/c').free-16*1024**2 >= 20*1024**3
assert shutil.disk_usage('/mnt/e').free-16*1024**2 >= 20*1024**3
original=Path('/mnt/e/xwn374/build001/default.xbe').read_bytes()
assert sha(original)=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
raw=(P/'boot_xbe/xbeboot.S').read_bytes()
assert sha(raw)=='b8ddf72f41a682d3868f1b801492b31005611c6868aa5927f54e5ce14bb94a2c'
source=raw.decode()
def replace(a,b):
    global source
    assert source.count(a)==1,repr(a)
    source=source.replace(a,b)
replace('.long 0x00060000', '.long '+hex(struct.unpack_from('<I',original,0x1084)[0]))
replace('\t.long\t0\t\t// end of table', '''DiagNtCreateFile: .long 0x80000000 + 190
DiagNtWriteFile: .long 0x80000000 + 236
DiagNtFlushBuffersFile: .long 0x80000000 + 198
DiagNtClose: .long 0x80000000 + 187
DiagHalReturnToFirmware: .long 0x80000000 + 49
\t.long\t0\t\t// end of table''')
replace('_start:\n', '_start:\n    pushfd\n    pop dword ptr [diag_record+16]\n')
replace('mov\t[kernelram], eax', '''mov\t[kernelram], eax
        mov dword ptr [diag_record+20], 1
        test eax, eax
        jnz 1f
        pop ecx
        pop ebx
        jmp diag_finish
1:''')
replace('    rep movsb\n    pop ecx', '''    pushfd
    pop dword ptr [diag_record+52]
    test dword ptr [diag_record+52], 0x400
    jz 2f
    mov dword ptr [diag_record+20], 5
    pop ecx
    jmp diag_finish
2:
    rep movsb
    pop ecx''')
replace('mov\t[bootloaderram], eax', '''mov\t[bootloaderram], eax
        mov dword ptr [diag_record+20], 2
        test eax, eax
        jnz 3f
        pop ecx
        pop ebx
        jmp diag_finish
3:''')
replace('mov\t[phys_bootloaderram],  eax', 'mov\t[phys_bootloaderram],  eax\n        mov [diag_record+56], eax')
replace('        call\tdword ptr [NtAllocateVirtualMemory]', '''        call\tdword ptr [NtAllocateVirtualMemory]
        mov [diag_record+40], eax
        mov dword ptr [diag_record+20], 3
        test eax, eax
        js 4f
        mov dword ptr [diag_record+20], 4
4:
        pop ecx
        pop ebx
        jmp diag_finish''')
replace('#include "font.S"', (K/'logger.S').read_text()+'\n#include "font.S"')
O.mkdir(parents=True)
for name in ['xbe.S','font.S']:
    shutil.copyfile(P/'boot_xbe'/name,O/name)
(O/'xbeboot.S').write_text(source)
cc=Path('/usr/bin/x86_64-linux-gnu-gcc-12')
assert sha(cc.read_bytes())=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
record=dict(status='building',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,
            original_xbe_sha256=sha(original),original_wrapper_sha256=sha(raw),
            source_sha256=sha((O/'xbeboot.S').read_bytes()),compiler_sha256=sha(cc.read_bytes()),
            actual_windows_boot=False,physical_access=False,attempt_cookie='40900101',
            pins={str(p):sha(p.read_bytes()) for p in [K/'build003.py',K/'logger.S',O/'xbe.S',O/'font.S',Path('/mnt/c/nxdk/lib/xboxkrnl/xboxkrnl.h'),Path('/mnt/c/nxdk/lib/xboxkrnl/xboxkrnl.exe.def'),Path('/mnt/c/nxdk/lib/hal/xbox.c')]})
def save():(K/'build003.json').write_text(json.dumps(record,indent=2)+'\n')
save()
try:
    cmds=[[str(cc),'-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'],
          ['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'],
          ['objcopy','-O','binary','wrapper.elf','wrapper.bin']]
    with (O/'build.log').open('w') as log:
        for cmd in cmds:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=30)
    prefix=(O/'wrapper.bin').read_bytes();assert len(prefix)==12288
    xbe=bytearray(prefix+original[12288:]);assert len(xbe)==len(original)
    # Retain all already-reviewed original header values, except new section hash.
    xbe[:4096]=original[:4096]
    section=struct.unpack_from('<I',xbe,0x120)[0]-0x10000
    assert section==840
    off,size=struct.unpack_from('<II',xbe,section+12);assert off==4096 and off+size==len(xbe)
    xbe[section+36:section+56]=hashlib.sha1(struct.pack('<I',size)+xbe[off:off+size]).digest()
    (O/'default.xbe').write_bytes(xbe)
    assert xbe[12288:]==original[12288:]
    assert xbe[0x1080:0x1088]==original[0x1080:0x1088], 'payload descriptor must retain actual imagebld size'
    record.update(status='compiled',bytes=len(xbe),sha256=sha(xbe),embedded_payload_unchanged=True,
                  commands=cmds,header_unchanged_except_section_digest=True)
except BaseException as e:record.update(status='failed',error=repr(e));raise
finally:save()
