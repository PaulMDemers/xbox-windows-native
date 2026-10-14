import subprocess,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;src=Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001/source');out=Path('/mnt/e/xwn388/source001');out.mkdir(parents=True,exist_ok=False)
tree='8e12297ca0ed53383fe9aaebef152c26aee5a43b';rows={}
for name in ['create.c','dir.c','fcb.c','direntry.c','vfat.h']:
 p='drivers/filesystems/vfatfs/'+name;b=subprocess.check_output(['git','-C',str(src),'show',tree+':'+p]);assert b==(src/p).read_bytes(),name
 (out/name).write_bytes(b);rows[name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r={'source_tree':tree,'binary_sha256':'ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9','build_evidence':'outputs/fatx-directory-order/build-report.json','private_capsule':'E:/xwn388/source001','files':rows,'scope':'Read-only exact historical build-tree source; candidate explanation, no patch/runtime result'}
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
s=(out/'direntry.c').read_text().splitlines()
for i,l in enumerate(s):
 if any(x in l for x in ['FatXGetNext','StartIndex','DirIndex']):print(str(i+1)+': '+l)
