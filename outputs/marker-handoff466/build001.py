"""Build new emulator-only two-marker diagnostic; preserve all predecessor bytes."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
O=Path('/mnt/c/xwn466/build001');P=Path('/mnt/e/xwn462/build001')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
parent=json.loads((K.parent/'boot-refusal462/build001.json').read_text())
assert sha((P/'default.xbe').read_bytes())==parent['sha256']
assert sha((P/'xbeboot.S').read_bytes())==parent['source_sha256']
core=K.parent/'entry-marker465/marker.S';host=json.loads((K.parent/'entry-marker465/host001.json').read_text())
assert host['status']=='passed' and sha(core.read_bytes())==host['source'][str(core)]
cc=Path('/usr/bin/x86_64-linux-gnu-gcc-12')
assert sha(cc.read_bytes())==host['compiler_sha256']
original=Path('/mnt/e/xwn374/build001/default.xbe').read_bytes()
oldpayload=Path('/mnt/e/xwn374/build001/image-crom.bin').read_bytes()
assert oldpayload==original[0x3000:0x3000+len(oldpayload)] and len(oldpayload)==288316
O.mkdir(parents=True)
helper=core.read_text().replace('.section .note.GNU-stack,"",@progbits','')
stub=(K/'after-stack.S').read_text()+'\n'+helper
(O/'stub.S').write_text(stub)
commands=[]
def run(cmd):
    commands.append(cmd)
    with (O/'build.log').open('a') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=f,check=True,timeout=30)
def syms(file):
    s=subprocess.check_output(['nm','-n',file],cwd=O,text=True)
    (O/(file+'.symbols.txt')).write_text(s)
    return {v[2]:int(v[0],16) for line in s.splitlines() if len(v:=line.split())==3}
r=dict(status='building',physical_access=False,physical_candidate_qualified=False,parent_sha256=parent['sha256'],source_pins={str(p):sha(p.read_bytes()) for p in [K/'build001.py',K/'after-stack.S',core,P/'xbeboot.S',P/'xbe.S',P/'font.S',cc]})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    run([str(cc),'-m32','-c','stub.S','-o','stub.o'])
    run(['ld','-m','elf_i386','-Ttext','0x02680000','-e','after_stack_stub','stub.o','-o','stub.elf'])
    run(['objcopy','-O','binary','stub.elf','stub.bin'])
    ss=syms('stub.elf');blob=(O/'stub.bin').read_bytes()
    assert ss['after_stack_stub']==0x2680000 and len(blob)<4096
    assert 0x265f048<ss['after_stack_stub']<ss['after_stack_stub']+len(blob)<0x2700000<0x2800000
    payload=bytearray(oldpayload);assert payload[0xf0:0xf5]==bytes.fromhex('bc00008002')
    payload[0xf0:0xf5]=b'\xe9'+struct.pack('<i',ss['after_stack_stub']-(0x26000f0+5))
    payload+=bytes(0x80000-len(payload))+blob
    (O/'payload.bin').write_bytes(payload)
    source=(P/'xbeboot.S').read_text().replace('462','466')
    old=f'.long {hex(len(oldpayload))}'
    assert source.count(old)==1;source=source.replace(old,f'.long {hex(len(payload))}')
    old='diag_handoff:\n    popad'
    new='''diag_handoff:
    mov dword ptr [diag_reason], 12
    push offset before_marker_record
    call marker_guarded
    add esp, 4
    mov eax, [before_marker_record+20]
    cmp eax, 1
    jne diag_reboot
diag_marker_ready:
    popad'''
    assert source.count(old)==1;source=source.replace(old,new)
    tail='''\n.balign 4
before_marker_record:
    .long 0x354b524d,1,96,1,0xff
    .zero 76
'''+helper+'\n'
    assert source.count('#include "font.S"')==1;source=source.replace('#include "font.S"',tail+'#include "font.S"')
    (O/'xbeboot.S').write_text(source)
    for name in ['xbe.S','font.S']:shutil.copyfile(P/name,O/name)
    run([str(cc),'-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
    run(['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'])
    run(['objcopy','-O','binary','wrapper.elf','wrapper.bin'])
    ws=syms('wrapper.elf');prefix=(O/'wrapper.bin').read_bytes();assert len(prefix)==0x3000
    assert ws['gdt_48_base']+4-ws['blentry']==224 and ws['ptr_newloc']-ws['blentry']==74 and ws['newloc']-ws['blentry']==80
    xbe=bytearray(prefix+payload+original[0x3000+len(oldpayload):]);xbe[:4096]=original[:4096]
    assert len(xbe)-len(payload)==len(original)-len(oldpayload)
    struct.pack_into('<I',xbe,0x10c,len(xbe))
    struct.pack_into('<I',xbe,0x350,len(xbe)-4096)
    struct.pack_into('<I',xbe,0x358,len(xbe)-4096)
    xbe[0x348+36:0x348+56]=hashlib.sha1(struct.pack('<I',len(xbe)-4096)+xbe[4096:]).digest()
    (O/'default.xbe').write_bytes(xbe)
    assert struct.unpack_from('<I',xbe,0x1084)[0]==len(payload)
    r.update(status='compiled',sha256=sha(xbe),bytes=len(xbe),payload_bytes=len(payload),payload_sha256=sha(payload),wrapper_symbols=ws,stub_symbols=ss,commands=commands,
             original_payload_changes=[dict(offset=i,old=oldpayload[i],new=payload[i]) for i in range(len(oldpayload)) if oldpayload[i]!=payload[i]],
             owned_tail=dict(start=0x2680000,end=0x2680000+len(blob),bss_end=0x265f048,copy_end=0x2700000,stack_top=0x2800000))
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
    r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in O.iterdir() if p.is_file()};save()
