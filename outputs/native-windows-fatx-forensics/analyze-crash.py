"""Read-only NT5 symbol and page-table analysis of the captured high-allocation crash."""
import bisect,json,pathlib,struct,sys
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import capstone
ram=(ws/'work/runs/nt5-physical-f-high-allocation-001/crash-memory.ram').read_bytes()
cr3=0x03257000;pc=0x824c7a22
def u32(at):return struct.unpack_from('<I',ram,at)[0]
def pa(va):
    pde=u32((cr3&~4095)+(va>>22)*4);assert pde&1
    if pde&128:return (pde&0xffc00000)+(va&0x3fffff)
    pte=u32((pde&~4095)+((va>>12)&1023)*4);assert pte&1
    return (pte&~4095)+(va&4095)
def read(va,n):return bytes(ram[pa(va+i)] for i in range(n))
images=[]
for p in range(0,len(ram)-4096,4096):
    if ram[p:p+2]!=b'MZ':continue
    off=u32(p+60)
    if off>3500 or ram[p+off:p+off+4]!=b'PE\0\0':continue
    ts=u32(p+off+8);size=u32(p+off+24+56)
    if ts==0x4b7a1bd5:
        va=0x80000000+p
        try:assert pa(va)==p
        except (AssertionError,struct.error):continue
        if va<=pc<va+size:images.append((va,size))
assert len(images)==1,images
base,size=images[0]
pub=json.loads((ws/'outputs/native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
symbols=sorted((v['rva'],name) for name,v in pub.items());rvas=[s[0] for s in symbols]
def symbol(va):
    if not base<=va<base+size:return None
    i=bisect.bisect_right(rvas,va-base)-1
    return dict(name=symbols[i][1],offset=va-base-symbols[i][0],start=hex(base+symbols[i][0]))
fault=symbol(pc);start=int(fault['start'],16)
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
instructions=[dict(address=hex(i.address),instruction=i.mnemonic+' '+i.op_str) for i in md.disasm(read(start,pc-start+32),start)]
frames=[];frame=0xfc095d18;seen=set()
for _ in range(24):
    if frame<0x80000000 or frame in seen:break
    seen.add(frame)
    try:values=struct.unpack('<8I',read(frame,32))
    except (AssertionError,struct.error,IndexError):break
    frames.append(dict(frame=hex(frame),words=[hex(v) for v in values],return_symbol=symbol(values[1])))
    # Stop at a trap-frame transition rather than mislabeling arbitrary pool
    # links as call frames. The original fault context is sought separately.
    if not symbol(values[1]):break
    frame=values[0]
contexts=[];at=0
while True:
    at=ram.find(struct.pack('<I',pc),at)
    if at<0:break
    if at>=0xb8 and u32(at+4)==8 and u32(at+8)&2:
        for kind,back in [('trap',0x68),('context',0xb8)]:
            start=at-back
            offsets={'eax':0x44,'ebp':0x60,'esi':0x58,'ecx':0x40,'edx':0x3c,'ebx':0x5c,'edi':0x54} if kind=='trap' else {'eax':0xb0,'ebp':0xb4,'esi':0xa0,'ecx':0xac,'edx':0xa8,'ebx':0xa4,'edi':0x9c}
            registers={name:hex(u32(start+off)) for name,off in offsets.items()}
            if int(registers['esi'],16)-0x10==0x006fffc8:
                context=dict(kind=kind,physical_record=hex(start),registers=registers,words_after_pc=[hex(u32(at+x)) for x in range(0,32,4)])
                bp=int(registers['ebp'],16)
                try:context['frame_words']=[hex(v) for v in struct.unpack('<12I',read(bp,48))]
                except (AssertionError,IndexError,struct.error):context['frame_unmapped']=True
                context['caller_frames']=[]
                for _ in range(8):
                    if not 0xfc096000<=bp<0xfc098000:break
                    try:words=struct.unpack('<12I',read(bp,48))
                    except (AssertionError,IndexError,struct.error):break
                    context['caller_frames'].append(dict(frame=hex(bp),words=[hex(v) for v in words],symbol=symbol(words[1])))
                    if words[0]<=bp:break
                    bp=words[0]
                contexts.append(context)
    at+=4
driver_images=[]
for va in range(0xfe442000,0xfe400000,-4096):
    try:
        head=read(va,4096)
        if head[:2]!=b'MZ':continue
        off=struct.unpack_from('<I',head,60)[0]
        if off>3500 or head[off:off+4]!=b'PE\0\0':continue
        image_size=struct.unpack_from('<I',head,off+24+56)[0]
        if va<=0xfe442cd6<va+image_size:driver_images.append(dict(base=hex(va),size=hex(image_size),caller_rva=hex(0xfe442cd6-va)))
    except (AssertionError,IndexError,struct.error):continue
r=dict(scope=__doc__,kernel_base=hex(base),kernel_size=hex(size),fault_pc=hex(pc),fault_symbol=fault,driver_image_candidates=driver_images,
       fault_is_instruction_boundary=any(i['address']==hex(pc) for i in instructions),instructions=instructions,frames=frames,matching_fault_context_candidates=contexts)
length,maximum,buffer=struct.unpack('<HHI',read(0xfc096b80,8))
r['rename_input']={'length':length,'maximum_length':maximum,'buffer':hex(buffer),
                   'text':read(buffer,length).decode('utf-16-le') if length<=84 else 'out of bound'}
r['rename_locals']={'caller_rva':'0x7cd6','function_from_matching_coff_symbols':'vfatRenameEntry',
                    'cache_context':hex(struct.unpack('<I',read(0xfc096a38,4))[0]),
                    'directory_entry_pointer':hex(struct.unpack('<I',read(0xfc096a3c,4))[0]),
                    'oem_string_words':[hex(x) for x in struct.unpack('<II',read(0xfc096a48,8))],
                    'caveat':'Post-fault locals, not a record of the CcPinRead return value.'}
(k/'high-crash-analysis.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
