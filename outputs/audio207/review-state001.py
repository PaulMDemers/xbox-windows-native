"""Actual NT5 imports and dynamic exports, including forwarded export chains."""
import hashlib,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'state-review001.json';assert not dest.exists()
def provider(name):
    name=name.lower()
    if '.' not in name:name+='.dll'
    for folder in ['state-providers001','install-providers001','inventory001']:
        p=k/'artifacts'/folder/name
        if p.exists():return p
    raise AssertionError(('Missing actual provider',name))
def resolve(module,symbol,seen=()):
    key=(module.lower(),symbol);assert key not in seen
    p=provider(module);pe=pefile.PE(str(p))
    matches=[v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if (v.ordinal==symbol if isinstance(symbol,int) else v.name==symbol.encode())]
    assert len(matches)==1,(module,symbol)
    value=matches[0];chain=[dict(module=p.name,sha256=sha(p),symbol=symbol)]
    if value.forwarder:
        target,fn=value.forwarder.decode().rsplit('.',1)
        chain+=resolve(target,int(fn[1:]) if fn.startswith('#') else fn,seen+(key,))
    return chain
rows=[]
for name in ['state','probe-installed','installed-runner']:
    p=k/'artifacts/state001'/(name+'.exe');pe=pefile.PE(str(p))
    assert pe.FILE_HEADER.Machine==0x14c
    assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
    imports=[]
    for library in pe.DIRECTORY_ENTRY_IMPORT:
        for item in library.imports:
            imports.append(resolve(library.dll.decode(),item.name.decode() if item.name else item.ordinal))
    rows.append(dict(name=p.name,sha256=sha(p),imports=imports))
dynamic=[resolve(m,s) for m,s in [('psapi.dll','EnumDeviceDrivers'),('psapi.dll','GetDeviceDriverBaseNameA'),('cfgmgr32.dll','CM_Get_DevNode_Status'),('setupapi.dll','CMP_WaitNoPendingInstallEvents')]]
inf=(k/'xwnaci207.inf').read_text();expected='PCI\\VEN_10DE&DEV_01B1&SUBSYS_00000000&REV_B1'
models=[line for line in inf.splitlines() if ',PCI\\' in line]
assert models==['%Device%=Audio,'+expected]
assert 'DEV_01B0' not in inf and 'DEV_01B4' not in inf
r=dict(passed=True,binaries=rows,dynamic_exports=dynamic,inf_sha256=sha(k/'xwnaci207.inf'),exact_model_id=expected,physical_qualified=False,installation_qualified=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('State helper PE imports and dynamic export chains resolved against actual NT5 files')
