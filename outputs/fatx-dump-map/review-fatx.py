"""Collect matched FATX builds and verify their imports, source and PE identity."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
kernel=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe')
assert sha(kernel)=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
hal=k.parent/'hal-dump-path/artifacts/hal-candidate001.dll'
assert sha(hal)==read(k/'hal-review.json')['candidate001']['sha256']
exports={name:{e.name for e in pefile.PE(str(path)).DIRECTORY_ENTRY_EXPORT.symbols if e.name} for name,path in [('ntoskrnl.exe',kernel),('hal.dll',hal)]};r={}
for case,folder,lockfile in [('control001','fatx-dump-control-001','control-inputs.json'),('candidate001','fatx-dump-map-001','inputs.json')]:
    path=Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/build')/folder
    build=read(path/'build-report.json');lock=read(k/lockfile)
    assert build['status']=='compiled' and build['verified_source_tree']==lock['result_tree'] and build['inputs_sha256']==sha(k/lockfile)
    assert len(build['artifacts'])==1
    target=k/'artifacts'/('fatx-'+case+'.sys')
    if target.exists():assert target.read_bytes()==(path/'artifacts/xwnfatx.sys').read_bytes()
    else:target.write_bytes((path/'artifacts/xwnfatx.sys').read_bytes())
    assert sha(target)==build['artifacts'][0]['sha256']
    (k/('fatx-build-'+case+'.json')).write_bytes((path/'build-report.json').read_bytes())
    p=pefile.PE(str(target));imports=[dict(dll=d.dll.decode(),name=i.name.decode() if i.name else str(i.ordinal)) for d in p.DIRECTORY_ENTRY_IMPORT for i in d.imports]
    assert all(i['dll'].lower() in exports and i['name'].encode() in exports[i['dll'].lower()] for i in imports)
    nm=subprocess.check_output(['wsl','-d','Ubuntu','--','/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-nm','/home/paul/xbox-windows-native/build/'+folder+'/artifacts/xwnfatx.sys'],text=True)
    names=['_VfatFileSystemControl']+(['_VfatQueryRetrievalPointers'] if case=='candidate001' else [])
    sites={}
    for n in names:
        rows=[line.split() for line in nm.splitlines() if line.endswith(' '+n)];assert len(rows)==1
        rva=int(rows[0][0],16)-p.OPTIONAL_HEADER.ImageBase;sec=p.get_section_by_rva(rva)
        sites[n]=dict(rva=hex(rva),section=sec.Name.rstrip(b'\0').decode(),discardable=bool(sec.Characteristics&0x02000000));assert not sites[n]['discardable']
    source_hash=sha(path/'source/drivers/filesystems/vfatfs/fsctl.c')
    assert source_hash==(sha(k/'artifacts/fsctl.c') if case=='candidate001' else read(k.parent/'dump-fsctl-trace/contract-review.json')['owned_source_sha256']['drivers/filesystems/vfatfs/fsctl.c'])
    r[case]=dict(name=target.name,sha256=sha(target),build=folder,source_tree=lock['result_tree'],source_sha256=source_hash,imports=imports,resident_functions=sites,checksum_valid=p.OPTIONAL_HEADER.CheckSum==p.generate_checksum())
    assert r[case]['checksum_valid']
assert read(k/'inputs.json')['profiles']==read(k/'control-inputs.json')['profiles']
assert read(k/'map-tests.json')['source_sha256']['dump-map.inc']==sha(k/'dump-map.inc')
r.update(scope=__doc__,physical_access=False,qualified=False,limits='Fresh matched builds; host algorithm tests and binary/source review do not qualify runtime extents or dump writing.')
(k/'fatx-review.json').write_text(json.dumps(r,indent=2)+'\n');print({c:r[c]['sha256'] for c in ['control001','candidate001']})
