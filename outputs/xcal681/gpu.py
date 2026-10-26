"""Fresh isolated execution of pinned legacy SetGPURegister machine code.
No native encoder implementation, boot, timing or Windows success is implied.
"""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; O=Path('C:/xwn681/gpu001')
assert not O.exists() and not (K/'gpu001.json').exists(); O.mkdir(parents=True)
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
root='/home/paul/xbox-windows-native/launcher677-validation002/default720'
r={'passed':False,'physical_access':False,'scope':'legacy SetGPURegister instruction fixture; indexed register model', 'cases':[]}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
try:
    sources=json.loads((K/'sources.json').read_text())
    for name,sha in sources['files'].items():
        data=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+'/source/'+name],timeout=15)
        assert hashlib.sha256(data).hexdigest()==sha,name
    binary=O/'image.bin'
    subprocess.run(['wsl','-d','Ubuntu','--','objcopy','-O','binary',root+'/source/obj/image-crom.elf','/mnt/c/xwn681/gpu001/image.bin'],check=True,timeout=20)
    blob=binary.read_bytes();r['binary_sha256']=hashlib.sha256(blob).hexdigest()
    syms=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+'/symbols.txt'],timeout=15).decode()
    sym={a[2]:int(a[0],16) for line in syms.splitlines() if len(a:=line.split())==3}
    for initial in [0,255,85,170]:
        uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
        uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob)
        base=0xfd000000;uc.mem_map(base,0x800000)
        end=0x027ef000;out=0x027e0000;sp=0x027fe000
        # Exact legacy Xcalibur HDTV branch:720x480,32-bit,779/524 totals.
        uc.mem_write(out,pack(720,720,738,779,480,489,489,524,524,4,3))
        uc.mem_write(sp,pack(end,out,base));uc.reg_write(x.UC_X86_REG_ESP,sp)
        regs=bytearray([initial]*256); selected=[0];writes=[]
        def access(uc,access,address,size,value,user):
            if address==base+0x6013d4 and access==u.UC_MEM_WRITE:selected[0]=value&255
            elif address==base+0x6013d5:
                if access==u.UC_MEM_READ:uc.mem_write(address,bytes([regs[selected[0]]]))
                else:regs[selected[0]]=value&255
            if access==u.UC_MEM_WRITE:writes.append([address-base,size,value])
        uc.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,base,base+0x7fffff)
        uc.emu_start(sym['SetGPURegister'],end,timeout=1000000,count=20000)
        assert uc.reg_read(x.UC_X86_REG_EIP)==end
        get=lambda off:struct.unpack('<I',uc.mem_read(base+off,4))[0]
        width=get(0x680838)+1;height=get(0x680818)+1;pitch=8*(((regs[0x19]&0xe0)<<3)|regs[0x13]);fmt=regs[0x28]&15
        assert (width,height,pitch,fmt)==(720,480,2880,3)
        assert get(0x680824)==779 and get(0x680804)==524
        assert 316160+pitch*height < 9*1024*1024
        # Common routine must not alter clocks, framebuffer start or encoder.
        assert all(off not in [0x680508,0x600800] for off,size,value in writes)
        r['cases'].append({'initial_crtc':initial,'width':width,'height':height,'pitch':pitch,'format':fmt,'writes':writes})
    r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:(K/'gpu001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS four isolated legacy Xcalibur geometry fixtures')
