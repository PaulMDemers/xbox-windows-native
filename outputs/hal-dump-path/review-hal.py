"""Collect matched rebuilt HALs, verify imports/resident dispatch and preserve build reports."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
kernel=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe')
assert sha(kernel)=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
exports={e.name for e in pefile.PE(str(kernel)).DIRECTORY_ENTRY_EXPORT.symbols if e.name};r={};source_hashes={}
for case,folder,lockfile in [('control001','hal-dump-control-001','control-inputs.json'),('candidate001','hal-dump-path-002','inputs.json')]:
    path=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build')/folder
    build=read(path/'build-report.json');lock=read(k/lockfile)
    assert build['status']=='compiled' and build['verified_source_tree']==lock['result_tree'] and build['inputs_sha256']==sha(k/lockfile)
    assert len(build['artifacts'])==1
    name='hal-'+case+'.dll';target=k/'artifacts'/name
    assert not target.exists();target.write_bytes((path/'artifacts/halxboxnt5.dll').read_bytes())
    assert sha(target)==build['artifacts'][0]['sha256']
    (k/('hal-build-'+case+'.json')).write_bytes((path/'build-report.json').read_bytes())
    source_hashes[case]=sha(path/'source/hal/halx86/legacy/halpnpdd.c')
    p=pefile.PE(str(target));imports=[dict(dll=d.dll.decode(),name=i.name.decode() if i.name else str(i.ordinal)) for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports]
    assert all(i['dll'].lower()=='ntoskrnl.exe' and i['name'].encode() in exports for i in imports)
    assert 'PoRegisterDeviceForIdleDetection' not in [i['name'] for i in imports]
    nm=subprocess.check_output(['wsl','-d','Ubuntu','--','/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm',str('/home/paul/xbox-windows-native/build/'+folder+'/artifacts/halxboxnt5.dll')],text=True,stderr=subprocess.DEVNULL)
    sites={}
    for namepart in ['_HalpDispatchPnp@8','_HalpDispatchPower@8']:
        lines=[line.split() for line in nm.splitlines() if line.endswith(' '+namepart)];assert len(lines)==1
        rva=int(lines[0][0],16)-p.OPTIONAL_HEADER.ImageBase;s=p.get_section_by_rva(rva)
        assert s.Name.rstrip(b'\0')==b'.text' and not s.Characteristics&0x02000000
        sites[namepart]=dict(rva=hex(rva),section='.text',discardable=False)
    disabled={}
    for n in ['XwnConfigureEntryProbe','XwnConfigureMapProbe']:
        entry=next(e.address for e in p.DIRECTORY_ENTRY_EXPORT.symbols if e.name==n.encode());assert p.get_data(entry,5)==bytes.fromhex('31c0c20800');disabled[n]=hex(entry)
    r[case]=dict(name=target.name,sha256=sha(target),build=folder,source_tree=lock['result_tree'],source_sha256=source_hashes[case],imports=imports,resident_functions=sites,disabled_probes=disabled,checksum_valid=p.OPTIONAL_HEADER.CheckSum==p.generate_checksum())
    assert r[case]['checksum_valid']
assert source_hashes['control001']=='bf9c66a313a7c372c81fbe923d2681cf6487b14907154dd92b92eb8d8d24bbe0'
assert source_hashes['candidate001']==sha(k/'artifacts/halpnpdd.c')
assert read(k/'inputs.json')['profiles']==read(k/'control-inputs.json')['profiles']
r.update(scope=__doc__,physical_access=False,qualified=False,limits='Matched build flags and reviewed root functions; no claim of installed-baseline byte identity, guest correctness or real crash-dump capability.')
(k/'hal-review.json').write_text(json.dumps(r,indent=2)+'\n');print({c:r[c]['sha256'] for c in ['control001','candidate001']})
