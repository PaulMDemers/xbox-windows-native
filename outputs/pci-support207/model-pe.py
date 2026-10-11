"""Run the already-built core002 x86 engine with only I/O/CRT boundaries hooked.

This is a compiled-function/device-model test, not Windows loader or driver proof.
The host PE rejected by Windows remains unchanged. No compiler/build operation.
"""
import struct,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP,UC_X86_REG_EIP,UC_X86_REG_EAX

def symbols(pe,data):
    table=pe.FILE_HEADER.PointerToSymbolTable; count=pe.FILE_HEADER.NumberOfSymbols
    strings=table+18*count; result={};i=0
    # pefile sorts sections by RVA; COFF section numbers use original header order.
    sections=sorted(pe.sections,key=lambda s:s.get_file_offset())
    while i<count:
        record=data[table+18*i:table+18*(i+1)]
        name,value,section,typ,storage,aux=struct.unpack('<8sIhHBB',record)
        if name[:4]==bytes(4):
            offset=struct.unpack_from('<I',name,4)[0];begin=strings+offset;end=data.index(0,begin)
            name=data[begin:end]
        else:name=name.rstrip(b'\0')
        if 1<=section<=len(sections):result[name.decode()]=pe.OPTIONAL_HEADER.ImageBase+sections[section-1].VirtualAddress+value
        i+=1+aux
    return result

def run(path,address,command,transport):
    data=path.read_bytes();pe=pefile.PE(data=data);syms=symbols(pe,data)
    u=Uc(UC_ARCH_X86,UC_MODE_32);base=pe.OPTIONAL_HEADER.ImageBase
    u.mem_map(base,(pe.OPTIONAL_HEADER.SizeOfImage+4095)&~4095);u.mem_write(base,pe.get_memory_mapped_image())
    stack=0x800000;buf=0x900000;stop=0xa00000
    for mem in (stack,buf,stop):u.mem_map(mem,0x10000)
    def put(at,value):u.mem_write(at,struct.pack('<I',value))
    def get(at):return struct.unpack('<I',u.mem_read(at,4))[0]
    def cstring(at):
        b=bytearray()
        for i in range(256):
            byte=u.mem_read(at+i,1)
            if byte==b'\0':return b.decode()
            b.extend(byte)
        raise AssertionError('Unbounded test string')
    def ret(value=0):
        sp=u.reg_read(UC_X86_REG_ESP);u.reg_write(UC_X86_REG_EAX,value)
        u.reg_write(UC_X86_REG_EIP,get(sp));u.reg_write(UC_X86_REG_ESP,sp+4)
    args=['model',str(address),str(command)]
    for i,arg in enumerate(args):
        p=buf+0x100+i*0x100;u.mem_write(p,arg.encode()+b'\0');put(buf+i*4,p)
    sp=stack+0x8000
    for i,v in enumerate((stop,3,buf)):put(sp+4*i,v)
    u.reg_write(UC_X86_REG_ESP,sp)
    hooks={syms[name]:name for name in ('_read8','_read16','_write8','_delay','_strtoul','_printf','___main')}
    result=[];last=[]
    def hook(machine,at,size,context):
        last.append(hex(at))
        if len(last)>12:last.pop(0)
        if at==stop:machine.emu_stop();return
        name=hooks.get(at)
        if not name:return
        frame=u.reg_read(UC_X86_REG_ESP)
        if name=='___main':ret()
        elif name=='_strtoul':ret(int(cstring(get(frame+4))))
        elif name=='_printf':
            assert cstring(get(frame+4))=='RESULT %u %u %u %u %u\n'
            result.append(dict(zip(('result','polls','attempts','status','data'),[get(frame+8+4*i) for i in range(5)])));ret()
        elif name=='_delay':transport('DELAY',0,0);ret()
        else:
            assert get(frame+4)==0
            offset=get(frame+8);assert offset in (0,2,4,6,8)
            if name=='_read8':ret(transport('R8',offset,0))
            elif name=='_read16':ret(transport('R16',offset,0))
            else:transport('W8',offset,get(frame+12)&255);ret()
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(syms['_main'],stop+1,count=3000000)
    except Exception as e:raise RuntimeError(str(e)+' EIP='+hex(u.reg_read(UC_X86_REG_EIP))+' last='+str(last)+' hooks='+str(hooks)) from e
    assert u.reg_read(UC_X86_REG_EIP)==stop and u.reg_read(UC_X86_REG_EAX)==0
    assert u.reg_read(UC_X86_REG_ESP)==sp+4 and len(result)==1
    return result[0]
