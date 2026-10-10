"""Check i386 NT5 PE imports, exact snapshot inputs, and package scope."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;attempt=sys.argv[1]
assert len(attempt)==8 and attempt.startswith('build') and attempt[5:].isdigit()
canon=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,str(canon/'work/python-packages'));import pefile
out=k/'artifacts'/attempt;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
providers={};imports={};files={}
def exports(name):
    paths=[v for root in [base,base/'drivers'] for v in root.iterdir() if v.name.lower()==name.lower()]
    if name.lower()=='hal.dll':paths=[base.parents[2]/'E/Applications/XWNFBoot/loader/halxboxnt5.dll']
    assert len(paths)==1,(name,paths)
    p=paths[0];pe=pefile.PE(str(p));providers[name.lower()]={'path':str(p),'sha256':sha(p),'fixture_path':p.relative_to(base.parents[2]).as_posix()}
    return {s.name.decode():s for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
for binary,subsystem in [('xwnxid.sys',1),('probe.exe',3)]:
    pe=pefile.PE(str(out/binary));assert pe.FILE_HEADER.Machine==0x14c
    assert pe.OPTIONAL_HEADER.Subsystem==subsystem
    assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
    assert pe.OPTIONAL_HEADER.AddressOfEntryPoint
    if subsystem==1:assert pe.OPTIONAL_HEADER.DATA_DIRECTORY[5].Size>0
    rows={}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        name=entry.dll.decode();available=exports(name);names=[i.name.decode() for i in entry.imports]
        assert all(n in available for n in names),(name,set(names)-set(available))
        rows[name]=names
        for n in names:
            if available[n].forwarder:
                module,symbol=available[n].forwarder.decode().rsplit('.',1);assert symbol in exports(module+'.dll')
    imports[binary]=rows;files[binary]=sha(out/binary)
assert any('HidRegisterMinidriver' in n for n in imports['xwnxid.sys'].values())
assert 'UpdateDriverForPlugAndPlayDevicesA' in exports('newdev.dll')
assert 'CMP_WaitNoPendingInstallEvents' in exports('setupapi.dll')
inputs={}
for name in ['driver.c','nt5hid.h','xid_hid.c','xid_hid.h','probe.c','xwnxid.inf','xid_wire.c','xid_wire.h']:
    original=k/name if not name.startswith('xid_wire') else k.parent/'usb-xid-capture/driver-core'/name
    assert sha(original)==sha(out/name),name;inputs[name]=sha(original)
inf=(out/'xwnxid.inf').read_text()
assert 'VID_FFFF' not in inf and inf.count('VID_045E&PID_0202')==1
assert 'device.idVendor!=0x045e || device.idProduct!=0x0202' in (out/'driver.c').read_text()
r=dict(passed=True,attempt=attempt,files=files,inputs=inputs,imports=imports,providers=providers,physical_access=False,runtime_qualified=False)
(k/(attempt+'-review.json')).write_text(json.dumps(r,indent=2)+'\n')
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS i386 NT5 subsystem/imports, exact source snapshot and emulator-only package')
