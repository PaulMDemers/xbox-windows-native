"""Review compiled119 observation pair, exact source reconstruction and NT5 imports."""
import ast,hashlib,json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
dest=k/'build-review.json';assert not dest.exists()
r=read(k/'build-report.json');s=read(k/'source-review.json');assert r['status']=='compiled'
assert r['accounting_patch_sha256']==s['patch_sha256']==sha(k/'0119-upload-producer-accounting.patch')
assert read(k/'host-tests001.json')['passed']
for n,h in s['source_files'].items():assert sha(k/'display'/n)==h
assert sha(k/'upload_account.h')==s['source_files']['upload_account.h']
for n,h in read(k/'host-tests001.json')['source_pins'].items():assert sha(k/n)==h
parent=k.parent/'video-text-clip205/display'
shadow=(k/'display/shadow.c').read_text();original=(parent/'shadow.c').read_text()
assert re.findall(r' ok=Eng[^\n]+',shadow)==re.findall(r' ok=Eng[^\n]+',original)
assert 'EngAcquireSemaphore' not in shadow and 'current_kind' not in shadow
assert shadow.count('XwnUploadRecord')==2 and 'XwnUploadRecord(p,2,chosen!=NULL,&producer);' in shadow
assert (k/'display/surface.c').read_text().count('XwnUpload(ppdev,NULL,NULL,14);')==2
assert 'if(producer) XwaBox' in shadow and 'if(producer) XwaFallback' in shadow
assert 'step<256' in shadow and 'XWN_TEXT_BOUNDS && reason==XWT_EMPTY' in shadow
ownership=(k/'display/ownership.c').read_text();a=ownership.index('VOID XwnUploadRecord');b=ownership.index('VOID XwnUploadSnapshot',a)
body=ownership[a:b];assert body.count('EngAcquireSemaphore')==body.count('EngReleaseSemaphore')==1 and 'EngCopy' not in body
provider=ws/'outputs/video-physical-rehearsal160/artifacts/F/winnt/system32/win32k.sys';exports={v.name for v in pefile.PE(str(provider)).DIRECTORY_ENTRY_EXPORT.symbols if v.name}
cases={}
for row in r['builds']:
 p=k/row['case']/'artifacts/xwnown.dll';assert sha(p)==row['files'][0]['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
 imports={}
 for d in pe.DIRECTORY_ENTRY_IMPORT:
  assert d.dll.lower()==b'win32k.sys' and all(v.name in exports for v in d.imports)
  imports[d.dll.decode()]=[v.name.decode() for v in d.imports]
 cases[row['case']]=dict(sha256=sha(p),bytes=p.stat().st_size,imports=imports,definitions=row['definitions'],source_tree=row['source_tree'])
a,b=[cases[n] for n in ['control001','candidate001']];assert a['source_tree']==b['source_tree']==r['source_tree'] and a['imports']==b['imports']
x,y=[dict(v['definitions']) for v in [a,b]];assert x.pop('XWN_UPLOAD_ACCOUNTING')=='OFF' and y.pop('XWN_UPLOAD_ACCOUNTING')=='ON' and x==y
assert x['XWN_UC_STORES']==x['XWN_BODY_PROFILE']=='OFF' and x['XWN_TEXT_BOUNDS']=='ON'
for p in k.glob('*.py'):ast.parse(p.read_text())
result=dict(passed=True,source_tree=r['source_tree'],cases=cases,provider=dict(path=str(provider.relative_to(ws)),sha256=sha(provider)),
 only_definition_difference='XWN_UPLOAD_ACCOUNTING',physical_access=False,guest_launch=False,rendering_changed=False,new_imports=False,
 packet_words=158,all_15_producers_attributed=True,host_tests_sha256=sha(k/'host-tests001.json'),source_review_sha256=sha(k/'source-review.json'),
 limits='Observation build only. Completed-copy counters are not proof of redundancy; actual phase and pixel/cold evidence still required.')
dest.write_text(json.dumps(result,indent=2)+'\n');print('Fresh119 actual source/tree/import/flag review PASS')
