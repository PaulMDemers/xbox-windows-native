"""Inventory001 ABI/export and narrowly read-only API review. No console access."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;pci=k.parent
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
dest=k/'build001-review.json';assert not dest.exists()
build=read(k/'build001.json');art=k/'artifacts/build001'
for row in build['files']:assert sha(art/row['name'])==row['sha256']
assert sha(k/'inventory.c')==sha(art/'inventory.c')
providers={}
for row in read(pci/'providers001.json')['files'].values():
    file=pci/'artifacts/providers001'/row['output']
    assert sha(file)==row['sha256'];providers[file.name.lower()]=file
for name,digest in read(pci/'providers002.json')['files'].items():
    if '/' in name:continue
    file=pci/'artifacts/providers002'/name;assert sha(file)==digest;providers[name.lower()]=file
allowed=set('CloseHandle CreateFileA ExitProcess FlushFileBuffers GetLastError GetModuleFileNameA WriteFile lstrlenA SetupDiGetClassDevsA SetupDiEnumDeviceInfo SetupDiGetDeviceRegistryPropertyA SetupDiDestroyDeviceInfoList CM_Get_Device_IDA CM_Get_DevNode_Status CM_Get_First_Log_Conf CM_Get_Next_Log_Conf CM_Get_Next_Res_Des CM_Get_Res_Des_Data_Size CM_Get_Res_Des_Data CM_Free_Log_Conf_Handle CM_Free_Res_Des_Handle'.split())
def resolve(dll,name,seen=()):
    key=(dll.lower(),name);assert key not in seen
    p=providers[key[0]];pe=pefile.PE(str(p))
    sym=next(v for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name and v.name.decode()==name)
    row=dict(dll=key[0],name=name,provider_sha256=sha(p),forward=sym.forwarder.decode() if sym.forwarder else None)
    if sym.forwarder:
        target,entry=sym.forwarder.decode().rsplit('.',1);row['resolved']=resolve(target+'.dll',entry,seen+(key,))
    return row
pe=pefile.PE(str(art/'inventory.exe'));imports=[]
for desc in pe.DIRECTORY_ENTRY_IMPORT:
    for item in desc.imports:
        assert item.name and item.name.decode() in allowed,item.name
        imports.append(resolve(desc.dll.decode(),item.name.decode()))
assert pe.FILE_HEADER.Machine==0x14c and [pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion]==[5,0]
assert sha(art/'observer.exe')=='d69deda03c943de6d9aa10f76eebaf4474c09368c60a639cbb49c1add7be1487'
dest.write_text(json.dumps(dict(passed=True,scope=__doc__,imports=imports,inventory_sha256=sha(art/'inventory.exe'),source_sha256=sha(k/'inventory.c'),observer_sha256=sha(art/'observer.exe'),physical_access=False),indent=2)+'\n')
print('Inventory001 read-only API/import review passed')
