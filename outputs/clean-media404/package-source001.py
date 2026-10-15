"""Create a PRIVATE allowlisted source review ZIP, not a public release/tag."""
import hashlib,json,re,zipfile
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=Path(__file__).resolve().parent
out=Path('C:/xwn404/source-review001');out.mkdir(parents=True,exist_ok=False)
export=out/'source';export.mkdir()
names=set(['README.md','NOTICE.md','LICENSE','CONTRIBUTING.md','.gitattributes'])
for folder in ['src','LICENSES','upstream']:
 names.update(p.relative_to(W).as_posix() for p in (W/folder).rglob('*') if p.is_file())
names.update('docs/'+n+'.md' for n in ['architecture','building','installation','display-configuration','troubleshooting','recovery-guide','development','licensing','provenance','validation','windows-media'])
names.update('tools/'+n for n in ['xwn.py','build_space.py','toolchain_receipt.py','setup-dependencies.py','xwn_image.py','configure-e-display.py','e-display-policy.json','check-repository.py','verify-media.py'])
names.update('tests/'+n for n in ['test_xwn.py','test_xwn_image.py','test_toolchain_receipt.py','test_verify_media.py'])
manifest={};byte_count=0
for name in sorted(names):
 src=W/name;assert src.is_file() and not src.is_symlink(),name
 b=src.read_bytes();assert b'\0' not in b and not b.startswith(b'MZ') and len(b)<5*1024**2,name
 assert not re.search(rb'C:/Users/Paul|/home/paul|192\.168\.|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----',b),name
 dest=export/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 manifest[name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};byte_count+=len(b)
for p in export.rglob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if '://' in target or target.startswith('#'):continue
  assert (p.parent/target.split('#')[0]).exists(),(p,target)
header={'schema':1,'scope':'Private source review; no binary distribution, public release or private history','files':manifest}
(export/'SOURCE-MANIFEST.json').write_text(json.dumps(header,indent=2)+'\n',encoding='utf-8')
def assemble(dest):
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(export.rglob('*')):
   if not p.is_file():continue
   i=zipfile.ZipInfo(p.relative_to(export).as_posix(),(2026,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16
   z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 with zipfile.ZipFile(dest) as z:
  assert set(z.namelist())==set(manifest)|{'SOURCE-MANIFEST.json'}
  for name in z.namelist():assert z.read(name)==(export/name).read_bytes()
 return hashlib.sha256(dest.read_bytes()).hexdigest()
a=out/'xwn-source-review404.zip';b=out/'repeat-source-review404.zip'
ha=assemble(a);assert ha==assemble(b)
result={'archive':str(a),'sha256':ha,'archive_bytes':a.stat().st_size,'entries':len(manifest)+1,'source_bytes':byte_count,'deterministic_packaging':True,'entry_readback_verified':True,'patterns_and_local_links_checked':True,'public_release':False,'scope':'Allowlisted sources/docs/tools only; patterns are not complete privacy/license clearance'}
with (K/'source-package001.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
