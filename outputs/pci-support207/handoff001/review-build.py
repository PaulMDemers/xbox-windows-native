"""Review reconstructed HAL ABI/imports and source-to-installed baseline differences."""
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
k=Path(__file__).resolve().parent;pci=k.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
r=read(k/'build001.json');assert r['status']=='compiled'
for name,digest in r['sources'].items():assert sha(k/name)==digest,name
assert sha(k/'0001-hal-shared-smbus.patch')==r['patch_sha256']
candidate=k/'artifacts/build001/halxboxnt5.dll';assert sha(candidate)==r['candidate_sha256']
pins=read(pci/'providers001.json');providers={}
for row in pins['files'].values():
    p=pci/'artifacts/providers001'/row['output'];assert sha(p)==row['sha256'];providers[p.name.lower()]=p
installed=providers['halxboxnt5.dll'];assert sha(installed)=='a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648'
base=k/'artifacts/build001/native/artifacts/halxboxnt5.dll'
assert sha(base)==next(v['sha256'] for v in r['baseline']['artifacts'] if v['name']=='halxboxnt5.dll')
old,b,pe=[pefile.PE(str(p)) for p in (installed,base,candidate)]
exports=lambda p:{v.name.decode():v.ordinal for v in p.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
assert all(exports(pe).get(n)==v for n,v in exports(old).items())
assert set(exports(pe))-set(exports(old))=={'XwnSmbusReadV1'}
imports=[]
for d in pe.DIRECTORY_ENTRY_IMPORT:
    provider=providers[d.dll.decode().lower()];symbols=pefile.PE(str(provider)).DIRECTORY_ENTRY_EXPORT.symbols
    for imp in d.imports:
        name=imp.name.decode() if imp.name else '#'+str(imp.ordinal)
        entry=next(v for v in symbols if (v.name and v.name.decode()==name) or name=='#'+str(v.ordinal))
        assert not entry.forwarder
        imports.append(dict(dll=d.dll.decode(),name=name,provider_sha256=sha(provider)))
assert pe.FILE_HEADER.Machine==0x14c and [pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion]==[5,0]
section_deltas=[]
for a,c in zip(old.sections,b.sections):
    assert a.Name==c.Name
    section_deltas.append(dict(name=a.Name.decode().rstrip('\0'),same_virtual_layout=(a.VirtualAddress,a.Misc_VirtualSize)==(c.VirtualAddress,c.Misc_VirtualSize),same_bytes=a.get_data()==c.get_data()))
result=dict(scope=__doc__,passed=True,candidate_sha256=sha(candidate),installed_sha256=sha(installed),baseline_sha256=sha(base),baseline_installed_byte_identical=sha(base)==sha(installed),baseline_section_comparison=section_deltas,existing_export_ordinals_preserved=True,new_export=exports(pe)['XwnSmbusReadV1'],imports=imports,tests=read(k/'tests001.json'),limits='Static and compiled core evidence only. Candidate has not booted, no physical use, no guarantee of successful reboot when the bus cannot become idle. Installed binary equality is reported explicitly; source reconstruction alone does not prove it.')
dest=k/'build-review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({key:result[key] for key in ('passed','candidate_sha256','baseline_installed_byte_identical','baseline_section_comparison')},indent=2))
