"""Build a separately logged pass-through diagnostic from the exact installed wrapper."""
import datetime, hashlib, json, os, shutil, struct, subprocess, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/build/resolution-e374-build001/source')
O=Path('/mnt/e/xwn462/build001')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'build001.json').exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(O.parent)
assert shutil.disk_usage('/mnt/c').free-16*1024**2 >= 20*1024**3
assert shutil.disk_usage('/mnt/e').free-16*1024**2 >= 20*1024**3
original=Path('/mnt/e/xwn374/build001/default.xbe').read_bytes()
assert sha(original)=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
raw=(P/'boot_xbe/xbeboot.S').read_bytes()
assert sha(raw)=='b8ddf72f41a682d3868f1b801492b31005611c6868aa5927f54e5ce14bb94a2c'
source=raw.decode()
assert source.count('mov\tecx, PAGE_SIZE / 4')==2
assert source.count('rep \tmovsb')>=3
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
        jz 4f
        pop ecx
        pop ebx
        jmp diag_finish
4:
        mov dword ptr [diag_record+20], 4''')
replace('// Copy to #4', '// Refuse unexpected mapping/layout before executing the original two copies.\n    cmp dword ptr [ptr_PAGE_SIZE], 4096\n    jne diag_bad_size\n    mov eax, [phys_bootloaderram]\n    cmp eax, [diag_record+56]\n    jne diag_bad_alias\n    add eax, 0x80000000\n    cmp eax, [bootloaderram]\n    jne diag_bad_mirror\n// Copy to #4')
replace('\tjmp\tedx;', '\tjmp diag_verify')
replace('#include "font.S"', (K/'verify.S').read_text()+'\n'+(K/'logger.S').read_text()+'\n#include "font.S"')
O.mkdir(parents=True)
for name in ['xbe.S','font.S']:
    shutil.copyfile(P/'boot_xbe'/name,O/name)
(O/'xbeboot.S').write_text(source)
cc=Path('/usr/bin/x86_64-linux-gnu-gcc-12')
assert sha(cc.read_bytes())=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
record=dict(status='building',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,
            original_xbe_sha256=sha(original),original_wrapper_sha256=sha(raw),
            source_sha256=sha((O/'xbeboot.S').read_bytes()),compiler_sha256=sha(cc.read_bytes()),
            actual_windows_boot=False,physical_access=False,handoff_intended=True,attempt_cookie='46200101',
            pins={str(p):sha(p.read_bytes()) for p in [K/'build001.py',K/'logger.S',K/'verify.S',O/'xbe.S',O/'font.S',Path('/mnt/c/nxdk/lib/xboxkrnl/xboxkrnl.h'),Path('/mnt/c/nxdk/lib/xboxkrnl/xboxkrnl.exe.def'),Path('/mnt/c/nxdk/lib/hal/xbox.c')]})
def save():(K/'build001.json').write_text(json.dumps(record,indent=2)+'\n')
save()
try:
    cmds=[[str(cc),'-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'],
          ['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'],
          ['objcopy','-O','binary','wrapper.elf','wrapper.bin']]
    with (O/'build.log').open('w') as log:
        for cmd in cmds:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=30)
    symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True)
    (O/'symbols.txt').write_text(symbols)
    syms={line.split()[2]:int(line.split()[0],16) for line in symbols.splitlines() if len(line.split())==3}
    assert 0 < syms['gdt_48_base']+4-syms['blentry'] < 1024
    assert 0 < syms['ptr_newloc']-syms['blentry'] < 1020
    record['loader_copy_bytes']=1024
    record['critical_loader_span']=syms['gdt_48_base']+4-syms['blentry']
    record['symbols']={n:syms[n] for n in ['blentry','ptr_newloc','newloc','gdt_48_base','diag_verify','diag_record','diag_trailer','diag_handoff','diag_reboot','_start','refusal_record','refusal_reboot']}
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
