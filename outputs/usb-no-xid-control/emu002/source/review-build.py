import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;attempt=sys.argv[1];out=k/'artifacts'/attempt
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages');import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32');providers={};imports={};binaries={}
def exports(name):
    paths=[p for p in base.iterdir() if p.name.lower()==name.lower()];assert len(paths)==1
    p=paths[0];providers[name.lower()]=dict(path=str(p),sha256=sha(p),fixture_path=p.relative_to(base.parents[2]).as_posix())
    return {s.name.decode():s for s in pefile.PE(str(p)).DIRECTORY_ENTRY_EXPORT.symbols if s.name}
for name in ['control.exe','wizard.exe']:
    pe=pefile.PE(str(out/name));assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==3
    assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
    imports[name]={};binaries[name]=sha(out/name)
    for e in pe.DIRECTORY_ENTRY_IMPORT:
        n=e.dll.decode();available=exports(n);names=[s.name.decode() for s in e.imports];assert set(names)<=set(available)
        imports[name][n]=names
        for symbol in names:
            if available[symbol].forwarder:
                dll,func=available[symbol].forwarder.decode().rsplit('.',1);assert func in exports(dll+'.dll')
assert 'CMP_WaitNoPendingInstallEvents' in exports('setupapi.dll')
assert 'NtQueryInformationProcess' in exports('ntdll.dll')
assert not any('hid' in n.lower() or 'newdev' in n.lower() for groups in imports.values() for n in groups)
inputs={}
for n in ['control.c','wizard006.c','policy.h','setup_gate201.h','restart_gate201.h','test-policy.c']:
    assert sha(k/n)==sha(out/n);inputs[n]=sha(k/n)
assert (out/'policy-result.txt').read_text().startswith('POLICY_CHECKS ')
r=dict(passed=True,attempt=attempt,files=binaries,inputs=inputs,imports=imports,providers=providers,policy_test=(out/'policy-result.txt').read_text().strip(),xid_driver_packaged=False,physical_access=False)
(k/'build-review.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,policy_test=r['policy_test'],binaries=binaries)))
