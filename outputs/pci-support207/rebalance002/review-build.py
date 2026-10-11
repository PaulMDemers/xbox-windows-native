"""Pin resource-only binaries and resolve actual NT5 imports and dynamic lookups."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
k=Path(__file__).resolve().parent;pci=k.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
providers={}
for row in read(pci/'providers001.json')['files'].values():
    p=pci/'artifacts/providers001'/row['output'];assert sha(p)==row['sha256'];providers[p.name.lower()]=p
for name,digest in read(pci/'providers002.json')['files'].items():
    if '/' not in name:
        p=pci/'artifacts/providers002'/name;assert sha(p)==digest;providers[name.lower()]=p
providers['hal.dll']=providers['halxboxnt5.dll']
cache={}
def resolve(dll,name,seen=()):
    key=(dll.lower(),name);assert key not in seen;p=providers[key[0]]
    if key[0] not in cache:cache[key[0]]=pefile.PE(str(p))
    v=next(v for v in cache[key[0]].DIRECTORY_ENTRY_EXPORT.symbols if (v.name and v.name.decode()==name) or name=='#'+str(v.ordinal))
    row=dict(dll=dll,name=name,provider_sha256=sha(p))
    if v.forwarder:
        target,symbol=v.forwarder.decode().rsplit('.',1);row['forward']=resolve(target+'.dll',symbol,seen+(key,))
    return row
build=read(k/'build001.json');rows=[]
for row in build['sources']:assert sha(k/row['name'])==row['sha256']
for row in build['files']:
    p=k/'artifacts/build001'/row['name'];assert sha(p)==row['sha256']
    if p.suffix not in ('.sys','.exe'):continue
    pe=pefile.PE(str(p))
    assert pe.FILE_HEADER.Machine==0x14c and [pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion]==[5,0]
    imports=[]
    for dll in pe.DIRECTORY_ENTRY_IMPORT:
        for v in dll.imports:imports.append(resolve(dll.dll.decode(),v.name.decode() if v.name else '#'+str(v.ordinal)))
    dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);dis.skipdata=True
    for sec in pe.sections:
        if sec.Characteristics&0x20000000:
            assert not any(v.mnemonic in ('in','out','insb','insw','insd','outsb','outsw','outsd') for v in dis.disasm(sec.get_data()[:sec.Misc_VirtualSize],sec.VirtualAddress))
    rows.append(dict(name=p.name,sha256=sha(p),imports=imports))
dest=k/'build-review001.json';assert not dest.exists()
assert sha(k/'artifacts/build001/xwnrsc.sys')=='3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92'
dest.write_text(json.dumps(dict(passed=True,scope=__doc__,binaries=rows,dynamic=[resolve('newdev.dll','UpdateDriverForPlugAndPlayDevicesA'),resolve('setupapi.dll','CMP_WaitNoPendingInstallEvents')]),indent=2)+'\n',encoding='utf-8')
print('Resource-only build: actual imports and no direct port I/O verified')
