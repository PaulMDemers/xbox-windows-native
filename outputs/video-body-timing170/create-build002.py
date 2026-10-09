"""Review precise113 patch and derive fresh matched builds from pinned112."""
import ast,difflib,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-clip-upload';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=json.loads((k/'source-review.json').read_text());review['source_files']={p.name:sha(p) for p in (k/'display').iterdir() if p.is_file()}
patch='';changed=[]
for name in sorted(review['source_files']):
 before=old/'display'/name;after=k/'display'/name
 if before.exists() and sha(before)==sha(after):continue
 changed.append(name);a=before.read_text().splitlines(keepends=True) if before.exists() else []
 b=after.read_text().splitlines(keepends=True);rel='win32ss/drivers/displays/framebuf/'+name
 patch+=''.join(difflib.unified_diff(a,b,fromfile='a/'+rel if before.exists() else '/dev/null',tofile='b/'+rel))
assert changed==['CMakeLists.txt','enable.c','framebuf.h','ownership.c','profile_math.h','shadow.c']
(k/'0113-body-timing.patch').write_bytes(patch.encode());review['patch_sha256']=sha(k/'0113-body-timing.patch');review['changed_files']=changed
(k/'source-review.json').write_text(json.dumps(review,indent=2)+'\n')
text=(old/'build.py').read_text()
text=text.replace("review=read(k/'patch-review.json')", "review=read(k.parent/'video-clip-upload/patch-review.json');profile=read(k/'source-review.json')")
text=text.replace("k/'0112-complex-clip-upload.patch'", "k.parent/'video-clip-upload/0112-complex-clip-upload.patch'")
text=text.replace("k/'display'/n", "k.parent/'video-clip-upload/display'/n")
line="  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()"
assert text.count(line)==1
text=text.replace(line,"  assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==profile['parent_tree']\n  assert sha(k/'0113-body-timing.patch')==profile['patch_sha256']\n  run(['git','-C',str(src),'apply','--index',str(k/'0113-body-timing.patch')],stdout=log,stderr=log)\n"+line)
text=text.replace("  for n,h in review['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h", "  for n,h in profile['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h")
text=text.replace("[('candidate001','ON')]","[('control001','OFF'),('candidate001','ON')]")
text=text.replace("defs['XBOX_NT5_SHARED_FRAMEBUFFER']=enabled", "defs['XBOX_NT5_SHARED_FRAMEBUFFER']='ON';defs['XWN_BODY_PROFILE']=enabled")
text=text.replace("parent_tree=review['parent_tree'],patch_sha256=review['patch_sha256']", "parent_tree=profile['parent_tree'],patch_sha256=profile['patch_sha256'],prerequisite112_sha256=review['patch_sha256']")
ast.parse(text);assert not (k/'build002.py').exists();(k/'build002.py').write_bytes(text.encode())
text=(old/'Build.ps1').read_text().replace('video-clip-upload-001','video-body-timing170-002');(k/'Build002.ps1').write_bytes(text.replace('/build.py','/build002.py').encode())
print('Precise113 diff and fresh matched compile commands reviewed')
