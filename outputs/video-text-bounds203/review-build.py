"""Pin actual paired 117 artifacts and NT5 imports; no runtime qualification."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'build-review.json';assert not dest.exists()
r=read(k/'build-report.json');s=read(k/'source-review.json');assert r['status']=='compiled'
assert r['text_patch_sha256']==s['patch_sha256']==sha(k/'0117-text-upload-bounds.patch')
for n,h in s['source_files'].items():assert sha(k/'display'/n)==h
assert sha(k/'text_bounds.h')==s['source_files']['text_bounds.h']
assert read(k/'host-tests.json')['passed']
provider=ws/'outputs/video-physical-rehearsal160/artifacts/F/winnt/system32/win32k.sys'
p=pefile.PE(str(provider));exports={v.name for v in p.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
cases={}
for b in r['builds']:
 case=b['case'];dll=k/case/'artifacts/xwnown.dll';assert sha(dll)==b['files'][0]['sha256']
 pe=pefile.PE(str(dll));imports={}
 assert pe.FILE_HEADER.Machine==0x14c
 for entry in pe.DIRECTORY_ENTRY_IMPORT:
  assert entry.dll.lower()==b'win32k.sys' and all(v.name in exports for v in entry.imports)
  imports[entry.dll.decode()]=[v.name.decode() for v in entry.imports]
 cases[case]=dict(sha256=sha(dll),bytes=dll.stat().st_size,imports=imports,definitions=b['definitions'],source_tree=b['source_tree'])
a,b=[cases[n] for n in ['control001','candidate001']]
assert a['imports']==b['imports'] and a['source_tree']==b['source_tree']
da,db=[dict(v['definitions']) for v in [a,b]]
assert da.pop('XWN_TEXT_BOUNDS')=='OFF' and db.pop('XWN_TEXT_BOUNDS')=='ON' and da==db
assert da['XWN_BODY_PROFILE']==da['XWN_UC_STORES']=='OFF'
shadow=(k/'display/shadow.c').read_text();ownership=(k/'display/ownership.c').read_text()
assert shadow.index('reason=XwtBounds')<shadow.index('ok=EngTextOut')<shadow.index('XwnTextRecord')
assert 'if(account) XwtCopy' in shadow and 'XWN_TEXT_BOUNDS && reason==XWT_EMPTY' in shadow
assert 'XwnUploadInternal(p,chosen,pco,&copied)' in shadow
assert 'CLIPOBJ_cEnumStart' in shadow and 'step<256' in shadow
assert 'EngAcquireSemaphore' not in shadow
source_tree=r['source_tree'];assert source_tree!=s['parent_tree']
result=dict(passed=True,source_tree=source_tree,cases=cases,provider=dict(path=str(provider.relative_to(ws)),sha256=sha(provider)),
 new_imports=False,only_definition_difference='XWN_TEXT_BOUNDS',host_tests_sha256=sha(k/'host-tests.json'),
 physical_access=False,guest_launch=False,runtime_qualified=False,limits='Compiled and source reviewed. Actual NT5 glyph pixels/copied bytes and cold integrity are still required.')
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('Matched117 compiled imports/source/definitions reviewed')
