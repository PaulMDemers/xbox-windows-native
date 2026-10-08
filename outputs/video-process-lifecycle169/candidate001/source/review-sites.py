"""Pin actual captured NT5 process sites and owned timing exports; no launch."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
prior=read(k.parent/'shutdown-createprocess/site-review.json');binaries={};sites=[]
for name,rel in [('kernel32.dll','video-physical-rehearsal160/artifacts/F/winnt/system32/kernel32.dll'),
                 ('ntoskrnl.exe','video-physical-review159/artifacts/F/winnt/system32/ntoskrnl.exe')]:
    p=k.parent/rel;pe=pefile.PE(str(p));expected=prior['kernel_sha256'] if name=='ntoskrnl.exe' else prior['binaries'][name]['sha256'];assert sha(p)==expected
    binaries[name]=dict(path=str(p.relative_to(ws)).replace('\\','/'),sha256=sha(p),preferred_base=pe.OPTIONAL_HEADER.ImageBase,
        timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
    for site in prior['sites']:
        if site['name'] not in ['CreateProcessInternalW','_NtRaiseHardError@24','_NtShutdownSystem@4'] or site['module']!=name:continue
        rva=site['rva'];assert pe.get_data(rva,3).hex()==site['bytes']
        base=pe.OPTIONAL_HEADER.ImageBase if name=='kernel32.dll' else 0x823d0000
        sites.append(dict(site,address=base+rva,validation_bytes=pe.get_data(rva,32).hex()))
assert len(sites)==3
layout=k.parent/'native-windows-nt5-kernel/process-layouts.json';pubs=k.parent/'native-windows-nt5-kernel/kernel-publics.json'
out=dict(binaries=binaries,sites=sites,kernel_base_expected=0x823d0000,thread_owner_offset=prior['thread_owner_offset'],
    layouts_sha256=sha(layout),publics_sha256=sha(pubs),ordinary_qualified=False,physical_access=False)
(k/'sites.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
win=k.parent/'video-physical-rehearsal160/artifacts/F/winnt/system32/win32k.sys';pe=pefile.PE(str(win));base=pe.OPTIONAL_HEADER.ImageBase
assert sha(win)=='414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
exports={v.name.decode():v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name};md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
timing=[]
for name in ['EngQueryPerformanceCounter','EngQueryPerformanceFrequency']:
    e=exports[name];assert not e.forwarder
    code=pe.get_data(e.address,96);instructions=[]
    for ins in md.disasm(code,base+e.address):
        instructions.append(dict(rva=ins.address-base,bytes=ins.bytes.hex(),instruction=ins.mnemonic+' '+ins.op_str))
        if ins.mnemonic.startswith('ret'):break
    assert instructions[-1]['instruction']=='ret 4'
    timing.append(dict(name=name,rva=e.address,bytes=code.hex(),instructions=instructions))
r=dict(captured_win32k_path=str(win.relative_to(ws)).replace('\\','/'),sha256=sha(win),exports=timing,
    nt5_source_contract_checked=False,runtime_contract_checked=False,driver_changed=False,
    limits='Actual captured exports/disassembly only; match DDK signature and runtime frequency/counter before instrumenting a new driver.')
(k/'timing-interface.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('Pinned3 process sites and actual NT5 timing exports; no guest access')
