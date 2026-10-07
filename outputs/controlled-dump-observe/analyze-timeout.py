"""Independent offline translation of the preserved crash RAM and callback chain."""
import hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash002'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(out/'timeout-snapshot.json');t=read(out/'trace.json');ramfile=out/'artifacts/timeout-ram.bin';assert sha(ramfile)==s['ram_sha256'];ram=ramfile.read_bytes();assert len(ram)==64*1024*1024
cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',s['monitor_registers'])[1],16);cr2=int(re.search(r'CR2=([0-9a-fA-F]+)',s['monitor_registers'])[1],16)
def phys32(a):assert 0<=a<=len(ram)-4;return struct.unpack_from('<I',ram,a)[0]
def page(a):
    pde=phys32((cr3&~4095)+(a>>22)*4);r=dict(va=hex(a),pde=hex(pde),present=False)
    if not pde&1:return r
    if pde&128:r.update(present=True,physical=(pde&0xffc00000)+(a&0x3fffff));return r
    pte=phys32((pde&~4095)+((a>>12)&1023)*4);r['pte']=hex(pte)
    if pte&1:r.update(present=True,physical=(pte&~4095)+(a&4095))
    return r
def memory(a,n):
    b=b''
    while n:
        p=page(a);assert p['present'],p;take=min(n,4096-(a&4095));b+=ram[p['physical']:p['physical']+take];a+=take;n-=take
    return b
def symbol(a):
    m=next((v for v in t['module_list'] if v['base']<=a<v['base']+v['size']),None)
    return dict(module=m['name'],base=hex(m['base']),rva=hex(a-m['base'])) if m else None
mods=read(k/'modules.json');pins=[]
for name in ['ndis.sys','nvnetnt5.sys']:
    p=out/'artifacts'/('after-'+name);row=next(v for v in read(out/'callback-binaries.json')['files'] if v['phase']=='after' and v['name']==name);assert sha(p)==row['sha256'];pe=pefile.PE(str(p));mods[name]=dict(path=str(p),sha256=sha(p),preferred_base=pe.OPTIONAL_HEADER.ImageBase)
def pin(a,n=32):
    m=symbol(a);assert m;mname=m['module'].lower();v=mods[mname];p=Path(v['path']);assert sha(p)==v['sha256'];pe=pefile.PE(str(p));rva=int(m['rva'],16);base=int(m['base'],16)
    while True:
        rel=[e.rva-rva for b in pe.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and rva<=e.rva<rva+n];end=max([n]+[v+4 for v in rel]);assert end<=96
        if n==end:break
        n=end
    raw=pe.get_data(rva,n);b=bytearray(raw)
    for off in rel:struct.pack_into('<I',b,off,(struct.unpack_from('<I',b,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    resident=memory(a,n);assert resident==b
    pins.append(dict(address=hex(a),**m,raw=raw.hex(),resident=resident.hex(),relocations=rel,sha256=v['sha256']))
active=[v for v in s['callbacks'] if v['state']==2];assert len(active)==1;cb=active[0];buf=int(cb['buffer'],16);raw=memory(buf,cb['length']);adapter,handler=struct.unpack_from('<2I',raw);pin(int(cb['callback'],16));pin(handler)
fault=symbol(cr2);assert fault;pe=pefile.PE(mods[fault['module'].lower()]['path']);rva=int(fault['rva'],16);section=next(v for v in pe.sections if v.VirtualAddress<=rva<v.VirtualAddress+v.Misc_VirtualSize)
cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);code=[dict(address=hex(v.address),bytes=v.bytes.hex(),instruction=v.mnemonic+' '+v.op_str) for v in cs.disasm(pe.get_data(rva,80),cr2)]
frames=[];ebp=int(s['registers']['EBP'],16);seen=set()
for _ in range(32):
    if not 0x80000000<=ebp<0xfffffff0 or ebp in seen:break
    seen.add(ebp)
    try:rawf=memory(ebp,32)
    except AssertionError:break
    nxt,ret=struct.unpack_from('<2I',rawf);frames.append(dict(ebp=hex(ebp),raw=rawf.hex(),return_address=hex(ret),return_module=symbol(ret)))
    if nxt<=ebp or nxt-ebp>65536:break
    ebp=nxt
syms=read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols'];bug=syms['_KiBugCheckData']['rva'];data=memory(0x823df000+bug,20)
r=dict(scope=__doc__,physical_access=False,snapshot_sha256=sha(out/'timeout-snapshot.json'),ram_sha256=sha(ramfile),cr3=hex(cr3),cr2=hex(cr2),fault_mapping=page(cr2),fault_module=fault,fault_section=section.Name.rstrip(b'\0').decode(),fault_section_characteristics=hex(section.Characteristics),fault_code=code,active_callback=cb,callback_buffer=raw.hex(),adapter=hex(adapter),miniport_handler=hex(handler),handler_module=symbol(handler),pins=pins,frames=frames,bugcheck_data=[hex(v) for v in struct.unpack('<5I',data)],halted='HLT=1' in s['monitor_registers'])
save=out/'timeout-analysis.json';assert not save.exists();save.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['cr2','fault_mapping','fault_module','fault_section','miniport_handler','handler_module','bugcheck_data','halted']},indent=2))
