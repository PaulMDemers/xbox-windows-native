"""Run the actual FATX deferred-write branch with modeled cache/MDL services."""
import argparse, pathlib, sys, struct, json, hashlib
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(k.parents[1]/'work/python-packages'))
import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP
p=argparse.ArgumentParser();p.add_argument('driver',type=pathlib.Path);p.add_argument('--expect-pinned',action='store_true');p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
pe=pefile.PE(str(a.driver));base=pe.OPTIONAL_HEADER.ImageBase
ns={};s=(k.parent/'native-windows-nt5-kernel/test-boundary.py').read_text()
exec(s[s.index('def symbols(p):'):s.index('sym=symbols(h)')],{'struct':struct},ns);symbols=ns['symbols'](pe)
CTX=0x800000;IRP=CTX+0x1000;FILE=CTX+0x2000;FCB=CTX+0x3000;DEV=CTX+0x4000;IOS=CTX+0x5000;GLOBAL=CTX+0x6000;MDL=CTX+0x7000;STOP=CTX+0x8000;SP=CTX+0xe000
def run(lock_status=0,prelocked=False):
    u=Uc(UC_ARCH_X86,UC_MODE_32);u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image());u.mem_map(CTX,0x10000)
    put=lambda at,v:u.mem_write(at,struct.pack('<I',v&0xffffffff))
    get=lambda at:struct.unpack('<I',u.mem_read(at,4))[0]
    calls=[];deferred=[];hooks={};done=[]
    def ret(n,v=0):
        sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,v);u.reg_write(UC_X86_REG_ESP,sp+4+n*4);u.reg_write(UC_X86_REG_EIP,get(sp))
    def args(n):return struct.unpack('<'+'I'*n,u.mem_read(u.reg_read(UC_X86_REG_ESP)+4,n*4))
    def canwrite():
        assert args(4)==(FILE,512,1,0);calls.append('CcCanIWrite');ret(4,0)
    def lock():
        assert args(3)==(IRP,512,0);calls.append('VfatLockUserBuffer')
        if not lock_status:put(IRP+4,MDL)
        ret(0,lock_status) # internal C helper is cdecl
    def defer():
        f,callback,context,unused,length,retrying=args(6)
        assert (f,context,unused,length,retrying)==(FILE,CTX,0,512,0)
        calls.append('CcDeferWrite');deferred.append({'mdl':get(IRP+4),'callback':hex(callback)})
        ret(6)
    def stop():done.append(True);u.emu_stop()
    hooks[STOP]=stop;hooks[symbols['_VfatLockUserBuffer']]=lock
    hooks[symbols['_vfatDirEntryGetFirstCluster']]=lambda:ret(0,2)
    for lib in pe.DIRECTORY_ENTRY_IMPORT:
        for imp in lib.imports:
            target=STOP+0x100+len(hooks)*16;put(imp.address,target)
            name=imp.name.decode()
            if name=='CcCanIWrite':hooks[target]=canwrite
            elif name=='CcDeferWrite':hooks[target]=defer
            else:
                def unexpected(n=name):raise AssertionError('Unexpected import '+n)
                hooks[target]=unexpected
    put(symbols['_VfatGlobalData'],GLOBAL);put(GLOBAL+4,0x900001)
    put(CTX,IRP);put(CTX+4,0x900002);put(CTX+8,DEV);put(CTX+12,1);put(CTX+0x20,IOS);put(CTX+0x28,FILE)
    put(FILE+12,FCB);put(FCB+0xe4,FCB+0xf00);put(FCB+0x10,65536);put(FCB+0x18,65536);put(DEV+0xc0,512)
    put(IOS+4,512);put(IRP+0x60,IOS);put(IRP+4,MDL if prelocked else 0)
    put(CTX+0xf000,CTX);put(SP,STOP);put(SP+4,CTX+0xf000)
    u.reg_write(UC_X86_REG_ESP,SP);u.hook_add(UC_HOOK_CODE,lambda u,pc,size,ctx:hooks[pc]() if pc in hooks else None)
    u.emu_start(symbols['_VfatWrite'],0,count=10000)
    assert done,'Function failed to return'
    result={'calls':calls,'deferred':deferred,'status':hex(u.reg_read(UC_X86_REG_EAX)),'caller_context':get(CTX+0xf000)}
    if a.expect_pinned:
        if lock_status:
            assert not deferred and result['status']==hex(lock_status) and result['caller_context']==CTX
        else:
            assert calls==['CcCanIWrite','VfatLockUserBuffer','CcDeferWrite'] and deferred[0]['mdl']==MDL
    else:assert calls==['CcCanIWrite','CcDeferWrite'] and deferred[0]['mdl']==0
    if deferred:
        assert result['status']=='0x103' and result['caller_context']==0
        # Switch modeled process mappings: the old user VA now names unrelated
        # data; the pinned MDL retains the caller's original system mapping.
        user=CTX+0xa000;system=CTX+0xb000
        u.mem_write(user,b'OTHER-PROCESS!!!');u.mem_write(system,b'ORIGINAL-WRITE!!')
        put(IRP+0x3c,user);u.mem_write(MDL+6,struct.pack('<H',1));put(MDL+12,system)
        put(SP,STOP);put(SP+4,IRP);put(SP+8,0);u.reg_write(UC_X86_REG_ESP,SP)
        u.emu_start(symbols['_VfatGetUserBuffer'],0,count=1000)
        result['worker_buffer_bytes']=bytes(u.mem_read(u.reg_read(UC_X86_REG_EAX),16)).decode()
        assert result['worker_buffer_bytes']==('ORIGINAL-WRITE!!' if a.expect_pinned else 'OTHER-PROCESS!!!'), (result,hex(u.reg_read(UC_X86_REG_EAX)))
    return result
cases=[run()]
if a.expect_pinned:cases += [run(lock_status=0xc000009a),run(prelocked=True)]
r={'scope':__doc__,'driver_sha256':hashlib.sha256(a.driver.read_bytes()).hexdigest(),'expect_pinned':a.expect_pinned,'cases':cases,'limitation':'Models cache/MDL services; proves branch ordering, not physical corruption causality.'}
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

