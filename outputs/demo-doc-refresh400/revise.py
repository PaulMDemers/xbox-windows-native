"""Documentation-only archive revision; preserve399 inputs and every payload byte."""
import hashlib,json,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=K.parent/'demo-integration399'
sys.path.insert(0,str(P))
from gates import validation
validation();assert json.loads((P/'accepted-state.json').read_text())['accepted']
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
guide=(W/'docs/BUILD-CURRENT.md').read_bytes();assert b'physical398 validated' in guide
results={}
for kind,record,directory in [('system','system001.json','system002'),('preview','package001.json','preview002')]:
 old=read(P/record);srcpath=Path(old['archive']);expected=old['sha256'] if kind=='system' else old['archive_sha256']
 with srcpath.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
 destdir=Path('C:/xwn399')/directory;assert not destdir.exists();destdir.mkdir()
 dest=destdir/srcpath.name
 with zipfile.ZipFile(srcpath) as src:
  names=src.namelist();assert len(names)==len(set(names))
  manifest=json.loads(src.read('MANIFEST.json'));key='files' if kind=='system' else 'file_manifest'
  original_guide=src.read('docs/BUILD.md');assert original_guide==(W/'docs/BUILD.md').read_bytes()
  manifest[key]['docs/BUILD.md']=dict(bytes=len(guide),sha256=sha(guide))
  manifest['documentation_revision']=dict(kit='demo-doc-refresh400',superseded_archive_sha256=expected,change='BUILD.md now identifies390 on0101 and physical398; no payload changes')
  if kind=='preview':manifest['reconstructed_system_bundle']=results['system']
  newmanifest=(json.dumps(manifest,indent=2)+'\n').encode()
  with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for n in names:
    b=guide if n=='docs/BUILD.md' else newmanifest if n=='MANIFEST.json' else src.read(n)
    info=zipfile.ZipInfo(n,(2026,10,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
  count=0
  with zipfile.ZipFile(dest) as z:
   assert z.namelist()==names
   for n in names:
    b=z.read(n);expectedbytes=guide if n=='docs/BUILD.md' else newmanifest if n=='MANIFEST.json' else src.read(n)
    assert b==expectedbytes,n
    if n!='MANIFEST.json':assert manifest[key][n]==dict(bytes=len(b),sha256=sha(b)),n
    count+=1
 with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 results[kind]=dict(archive=str(dest),bytes=dest.stat().st_size,sha256=digest,entries=count,readback_verified=True,only_docs_and_manifest_changed=True,source_archive_sha256=expected,public_ready=False,restore_tested=False,fresh_console_capture=False)
 if kind=='system':results[kind].update(payload_files=old['payload_files'],protected_current_files_matched=old['protected_current_files_matched'],historical_registry_and_user_data=True)
 # Re-read parent archive after revision; never alter prior artifacts.
 with srcpath.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
result=dict(completed=True,hardware_writes=False,driver_changes=False,original399_inputs_unchanged=True,
 corrected_guide_sha256=sha(guide),script_sha256=sha(Path(__file__).read_bytes()),archives=results)
p=K/'revision001.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
