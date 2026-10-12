"""Identify loaded images and decode the private snapshot without guest access."""
import hashlib,importlib.util,json,re,struct,sys,traceback
from pathlib import Path
from walk import read_virtual,physical,scan_directory,ranges
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=out/'mapping.json';assert not dest.exists()
r=dict(passed=False,physical_access=False,ordinary_qualified=False,pins=[])
try:
    s=read(out/'snapshot.json');assert s['status']=='captured' and s['resumed']
    raw=Path(s['path']);assert sha(raw)==s['sha256'];data=raw.read_bytes();assert len(data)==67108864
    plan=read(k/'plan.json');cr3=s['control_registers']['CR3'];r['snapshot_sha256']=s['sha256']
    rv=lambda a,n:read_virtual(data,cr3,a,n)
    u=lambda a:struct.unpack('<I',rv(a,4))[0]
    pub=read(ws/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols']
    match=re.search(r'IDT=\s*([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',s['register_text']);assert match
    spec=importlib.util.spec_from_file_location('discovery',k/'kernel-discovery.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
    base,gates=d.discover(rv,int(match[1],16),int(match[2],16),{v:plan['public_symbols'][n] for v,n in [(0,'_KiTrap00'),(14,'_KiTrap0E')]})
    r.update(kernel_base=base,idt_gates=gates)
    pes={}
    for n,m in plan['modules'].items():
        assert sha(Path(m['path']))==m['sha256'];pes[n]=pefile.PE(m['path'])
    def header(n,b):
        pe=pes[n];assert rv(b,2)==b'MZ';off=u(b+60);assert 0x40<=off<4096
        assert rv(b+off,4)==b'PE\0\0' and u(b+off+8)==pe.FILE_HEADER.TimeDateStamp
        assert u(b+off+0x50)==pe.OPTIONAL_HEADER.SizeOfImage
    def pin(n,b,a,size):
        pe=pes[n];expected=bytearray(pe.get_data(a,size));assert len(expected)==size
        for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]):
            for e in block.entries:
                if e.type==3 and a<=e.rva<a+size:
                    o=e.rva-a;assert o+4<=size
                    struct.pack_into('<I',expected,o,(struct.unpack_from('<I',expected,o)[0]+b-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
        actual=rv(b+a,size);assert actual==expected,(n,hex(a),'resident code mismatch')
        r['pins'].append(dict(module=n,base=b,rva=a,size=size,sha256=hashlib.sha256(actual).hexdigest()))
    header('ntoskrnl.exe',base)
    for n in ['_KiTrap00','_KiTrap0E']:pin('ntoskrnl.exe',base,plan['public_symbols'][n],16)
    # This exact owned function reads the run count at0 and8-byte run pairs at8/12.
    mr=plan['modules']['ntoskrnl.exe']['exports']['MmGetPhysicalMemoryRanges']
    code=pes['ntoskrnl.exe'].get_data(mr,192)
    assert bytes.fromhex('ff74f808') in code and bytes.fromhex('ff74f80c') in code
    pin('ntoskrnl.exe',base,mr,192)
    L=plan['structures']['_LDR_DATA_TABLE_ENTRY']['fields'];off=lambda n:L[n]['offset']
    head=base+plan['public_symbols']['_PsLoadedModuleList'];q=u(head);prev=head;seen=set();mods=[]
    while q!=head:
        assert q not in seen and len(seen)<128 and u(q+4)==prev;seen.add(q);node=q-off('InLoadOrderLinks')
        length,maximum,ptr=struct.unpack('<HHI',rv(node+off('BaseDllName'),8));assert length%2==0 and 0<length<=maximum<=2048
        mods.append(dict(name=rv(ptr,length).decode('utf-16le').lower(),base=u(node+off('DllBase')),size=u(node+off('SizeOfImage'))))
        prev=q;q=u(q)
    assert u(head+4)==prev;r['modules']=mods
    for name in ['bootvid.dll','xboxvnt5.sys']:
        m=next(v for v in mods if v['name']==name);header(name,m['base'])
        section=next(t for t in pes[name].sections if t.Name.rstrip(b'\0')==b'.text')
        pin(name,m['base'],section.VirtualAddress,section.Misc_VirtualSize)
    boot=next(v['base'] for v in mods if v['name']=='bootvid.dll');syms=plan['modules']['bootvid.dll']['symbols']
    names=['Size','Version','Address','Physical','ReservedBytes','VisibleBytes','Width','Height','Stride','HiddenOffset','CacheType']
    view=dict(zip(names,struct.unpack('<11I',rv(boot+syms['_Published'],44))))
    state={n:u(boot+a) for n,a in syms.items() if n!='_Published'};r.update(view=view,provider_state=state)
    assert view==dict(Size=44,Version=2,Address=view['Address'],Physical=0x03700000,ReservedBytes=0x900000,
                     VisibleBytes=720*480*4,Width=720,Height=480,Stride=2880,HiddenOffset=0x900000-316160,CacheType=0)
    assert state['_Ready']==1 and state['_Owner'] and state['_References']>=1 and state['_FrameBufferStart']==view['Address']
    block=u(base+plan['public_symbols']['_MmPhysicalMemoryBlock']);count,total=struct.unpack('<II',rv(block,8));assert 0<count<=64
    runs=[dict(base_page=a,page_count=b) for a,b in struct.iter_unpack('<II',rv(block+8,8*count))]
    assert sum(v['page_count'] for v in runs)==total and all(v['page_count'] and v['base_page']+v['page_count']<=16384 for v in runs)
    excluded=all(v['base_page']+v['page_count']<=0x3700 or v['base_page']>=0x4000 for v in runs)
    high=u(base+pub['_MmHighestPhysicalPage']['rva']);low=u(base+pub['_MmLowestPhysicalPage']['rva'])
    pfn_db=u(base+plan['public_symbols']['_MmPfnDatabase'])
    r['physical_memory']=dict(pointer=block,runs=runs,total_pages=total,lowest_pfn=low,highest_pfn=high,pfn_database=pfn_db,
                              reserved_pages_excluded_from_runs=excluded,reserved_pages=2304)
    assert excluded,'Framebuffer is registered as physical memory'
    # Never read past the actual PFN database high-water mark.
    locations={};meta=[]
    for pfn in range(0x3700,min(high+1,0x4000)):
        b=rv(pfn_db+pfn*plan['structures']['_MMPFN']['size'],24)
        word=struct.unpack_from('<I',b,plan['structures']['_MMPFN']['fields']['u3']['offset'])[0]
        location=(word>>plan['pfn_page_location']['position'])&7;locations[str(location)]=locations.get(str(location),0)+1
        meta.append(b)
    r['physical_memory'].update(in_range_pfn_entries=len(meta),page_location_histogram=locations,
                                pfn_metadata_sha256=hashlib.sha256(b''.join(meta)).hexdigest())
    assert not any(locations.get(str(n),0) for n in [0,1,2]),'Reserved PFN appears zero/free/standby'
    process_layout=read(ws/'outputs/video-cache-handoff/process-layouts.json');f=process_layout['_EPROCESS']['fields'];kf=process_layout['_KPROCESS']['fields']
    head=base+pub['_PsActiveProcessHead']['rva'];q=u(head);prev=head;seen=set();procs=[]
    while q!=head:
        assert q not in seen and len(seen)<128 and u(q+4)==prev;seen.add(q);p=q-f['ActiveProcessLinks']['offset']
        procs.append(dict(pid=u(p+f['UniqueProcessId']['offset']),cr3=u(p+f['Pcb']['offset']+kf['DirectoryTableBase']['offset'])))
        prev=q;q=u(q)
    assert u(head+4)==prev;r['processes']=procs
    roots=sorted({cr3&0xfffff000}|{p['cr3']&0xfffff000 for p in procs});summary=[];all_dirs=[]
    for root in roots:
        scan=scan_directory(data,root);groups=ranges(scan['matches']);scan['ranges']=groups;all_dirs.append(scan)
        direct=[v for v in scan['matches'] if view['Address']<=v['virtual']<view['Address']+0x900000]
        assert sum(v['length'] for v in direct)==0x900000
        assert all(v['physical']==0x3700000+v['virtual']-view['Address'] and v['pcd'] and v['pwt'] and not v['pat'] and not v['user'] for v in direct)
        for v in scan['matches']:assert v['pcd'] and v['pwt'] and not v['pat'],'Additional present mapping is not UC'
        summary.append(dict(root=root,ranges=groups,pdes_examined=scan['pdes_examined'],ptes_examined=scan['ptes_examined']))
    private=Path('D:/xwn302/capture001/aliases.json');assert not private.exists();private.write_text(json.dumps(all_dirs,indent=2)+'\n')
    r.update(passed=True,roots=summary,private_aliases_sha256=sha(private),boundary_physical={str(o):physical(data,cr3,view['Address']+o) for o in [0,view['VisibleBytes']-1,view['HiddenOffset'],0x900000-1]})
except Exception as exc:r.update(error=repr(exc),traceback=traceback.format_exc())
r['limits']='Current snapshot/current and linked active roots only. No TLB/MSR/future-alias proof. No native GPU ownership or physical qualification.'
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','error','view','physical_memory'] if n in r},indent=2))
