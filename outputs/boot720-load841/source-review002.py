"""Finalize pre-launch observer review; preserve prior source tree and failures."""
from pathlib import Path
import difflib,hashlib,json,subprocess
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native/boot720841-source002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'source001.json').read_text());p=B/'fatx/drivers/filesystems/vfatfs/load841.c'
before=sha(p);p.write_bytes((K/'load841.c').read_bytes())
subprocess.run(['git','-C',str(B/'fatx'),'add','drivers/filesystems/vfatfs/load841.c'],check=True)
r['previous_fatx_tree']=r['trees']['fatx'];r['trees']['fatx']=subprocess.check_output(['git','-C',str(B/'fatx'),'write-tree'],text=True).strip()
r['observer_review']={'before_sha256':before,'after_sha256':sha(p),'reason':'Cache-manager stream file objects may have empty FileName; identify by stable FCB PathNameU while read resources are held. Bound optional EOF-byte inspection by returned<=requested.'}
(K/'source002.json').write_text(json.dumps(r,indent=2)+'\n')
for label in ['cromwell','reactos','fatx']:
 patch=K/(label+'.patch');(K/(label+'-preparation001.patch')).write_bytes(patch.read_bytes())
 parent=Path(r['parents'][label]['path']);dst=B/label;parts=[]
 names=subprocess.check_output(['git','-C',str(dst),'ls-files'],text=True).splitlines()
 for name in names:
  a=parent/name;b=dst/name
  if not a.exists() or a.read_bytes()!=b.read_bytes():
   old=a.read_text(encoding='latin1') if a.exists() else ''
   new=b.read_text(encoding='latin1');parts.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),'a/'+name,'b/'+name))
 for name in subprocess.check_output(['git','-C',str(parent),'ls-files'],text=True).splitlines():
  if not (dst/name).exists():parts.extend(difflib.unified_diff((parent/name).read_text(encoding='latin1').splitlines(True),[],'a/'+name,'b/'+name))
 patch.write_text(''.join(parts),encoding='latin1')
print('841 reviewed source pinned; prior tree/build retained')
