"""Review actual paired PEs and pin compiled host evidence before guest staging."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archive=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
build=read(k/'build-report.json');assert build['status']=='compiled'
assert sha(k/'0106-shared-uc-framebuffer.patch')==build['patch_sha256']
assert read(k/'host-tests.json')['passed']
report=dict(passed=False,build_sha256=sha(k/'build-report.json'),host_tests=read(k/'host-tests.json'),host_pins={n:sha(k/n) for n in ['tests/provider.c','tests/ntddk.h','xwn_fb.c','xwn_fb.h','artifacts/provider-test','host-tests.json']},cases=[])
provider={b'XwnFbAcquire',b'XwnFbRelease',b'XwnFbReleaseOwner'}
old_exports=None
for case in ['control001','candidate001']:
    row=read(k/case/'build.json');pes={}
    for f in row['files']:
        p=k/case/'artifacts'/f['name'];assert sha(p)==f['sha256'];pes[f['name']]=pefile.PE(str(p))
        assert pes[f['name']].OPTIONAL_HEADER.CheckSum==pes[f['name']].generate_checksum()
    boot=pes['xboxbvid.dll'];video=pes['xboxvnt5.sys']
    exported={e.name:e.ordinal for e in boot.DIRECTORY_ENTRY_EXPORT.symbols}
    if case=='control001':old_exports=exported;assert len(exported)==11
    else:
        assert all(exported.get(n)==v for n,v in old_exports.items())
        assert set(exported)==set(old_exports)|provider
    imports={};targets={}
    for name,pe in pes.items():
        imports[name]={}
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll=entry.dll.decode().lower();imports[name][dll]=[i.name.decode() for i in entry.imports]
            if dll=='bootvid.dll':target=boot;targets[dll]=sha(k/case/'artifacts/xboxbvid.dll')
            else:
                p=next(p for base in [archive,archive/'drivers'] for p in base.iterdir() if p.name.lower()==dll)
                target=pefile.PE(str(p));targets[dll]=sha(p)
            names={e.name for e in target.DIRECTORY_ENTRY_EXPORT.symbols}
            assert all(i.name and i.name in names for i in entry.imports),(name,dll)
    vi=imports['xboxvnt5.sys']
    if case=='candidate001':
        assert set(vi['bootvid.dll'])=={n.decode() for n in provider}
        assert not {'VideoPortMapMemory','VideoPortUnmapMemory'} & set(vi.get('videoprt.sys',[]))
    else:assert 'bootvid.dll' not in vi
    report['cases'].append(dict(case=case,exports={n.decode():v for n,v in exported.items()},imports=imports,targets=targets,files=row['files']))
report.update(passed=True,limitations='PE exports/imports and host exclusion model only; actual NT5 loader/IRQL/ownership order requires guest evidence. No concurrent publication contract: one boot initializer publishes before consumers.')
(k/'pe-review.json').write_text(json.dumps(report,indent=2)+'\n')
print('Paired export/import and host evidence review passed')
