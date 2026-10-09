"""Exact owned binary contracts; user addresses are leads until runtime pins."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((k.parent/'video-process-lifecycle169/sites.json').read_text())
r=dict(old);r['binaries']={name:dict(row) for name,row in old['binaries'].items()}
r['binaries']['umpnpmgr.dll']['path']=(k/'artifacts/umpnpmgr.dll').relative_to(ws).as_posix()
r['sites']=[dict(s) for s in old['sites']]
for s in r['sites']:
    if s['kind']=='create':s['kind']='create_inner'
prior=json.loads((k.parent/'shutdown-createprocess/site-review.json').read_text())
specs={'advapi32.dll':[('CreateProcessAsUserW',11,'create_outer')],
       'ntdll.dll':[('LdrInitializeThunk',0,'loader_entry'),('NtRaiseHardError',6,'harderror'),('NtTerminateProcess',2,'terminate')]}
dis=[]
for name,rows in specs.items():
    p=k/'artifacts'/name;pe=pefile.PE(str(p));assert sha(p)==prior['binaries'][name]['sha256']
    r['binaries'][name]=dict(path=p.relative_to(ws).as_posix(),sha256=sha(p),preferred_base=pe.OPTIONAL_HEADER.ImageBase,
                            timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
    exports={e.name.decode():e for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name}
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    for symbol,argc,kind in rows:
        e=exports[symbol];assert not e.forwarder
        raw=pe.get_data(e.address,32)
        r['sites'].append(dict(name=symbol,module=name,rva=e.address,address=pe.OPTIONAL_HEADER.ImageBase+e.address,
                               argc=argc,kind=kind,validation_bytes=raw.hex()))
        dis.append(dict(module=name,name=symbol,rva=e.address,instructions=[dict(rva=i.address-pe.OPTIONAL_HEADER.ImageBase,bytes=i.bytes.hex(),instruction=i.mnemonic+' '+i.op_str) for i in md.disasm(raw,pe.OPTIONAL_HEADER.ImageBase+e.address)]))
r['teb_offset']=prior['teb_offset'];r['last_error_offset']=0x34
r['limits']='Create inner/outer argc11 both stdcall48-byte stack delta. Loader entry symbol only: no APC argument semantics inferred. Preferred user addresses are leads; require loader identity or actual readable PE metadata AND resident relocated bytes on hits. No guest-data/register writes.'
(k/'sites.json').write_text(json.dumps(r,indent=2)+'\n')
(k/'site-disassembly.json').write_text(json.dumps(dis,indent=2)+'\n')
print('Pinned7 process/loader/error sites from actual owned binaries')
