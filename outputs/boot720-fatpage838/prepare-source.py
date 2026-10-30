"""Fresh source-only838: page-sized FATX metadata windows, unchanged720p."""
import difflib,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-cache837'
B=Path('/home/paul/xbox-windows-native/boot720838-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((A/'source002.json').read_text())
r={'physical_access':False,'space':require_space(B,22),'parents':{},'changes':{},'trees':{},'cache_sites':old['cache_sites']}
for label,tree in old['trees'].items():
 p=Path('/home/paul/xbox-windows-native/boot720837-source001')/label
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True)
 subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}
def change(label,path,new):
 p=B/label/path;before=p.read_text();h=sha(p);assert new!=before;p.write_text(new)
 r['changes'][label+'/'+path]={'before':h,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),new.splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c'),('reactos','boot/freeldr/freeldr/ntldr/winldr.c')]:
 t=(B/label/path).read_text();change(label,path,t.replace('837','838'))
fd='drivers/filesystems/vfatfs/'
for p in sorted((B/'fatx'/fd).iterdir()):
 if p.is_file() and p.suffix in ['.c','.h','.txt']:
  t=p.read_text()
  if '837' in t:change('fatx',fd+p.name,t.replace('837','838'))
for ext in ['c','h']:(B/'fatx'/fd/('cache837.'+ext)).rename(B/'fatx'/fd/('cache838.'+ext))
p=B/'fatx'/fd/'fat.c';t=p.read_text()
a=t.index('#define  CACHEPAGESIZE(');b=t.index('\n\n',a)
replacement='''/* FATX table length is rounded to 4 KiB, independently of data clusters.
 * A cluster-sized final cache window can extend beyond the FAT stream.
 * Use one cache page for FATX metadata; retain standard FAT behavior. */
#define CACHEPAGESIZE(pDeviceExt) \\
    (((pDeviceExt)->FatInfo.FatType == FATX16 || \\
      (pDeviceExt)->FatInfo.FatType == FATX32) ? PAGE_SIZE : \\
     ((pDeviceExt)->FatInfo.BytesPerCluster > PAGE_SIZE ? \\
      (pDeviceExt)->FatInfo.BytesPerCluster : PAGE_SIZE))'''
change('fatx',fd+'fat.c',t[:a]+replacement+t[b:])
r['repair_scope']='FATX16/32 table get/count/allocate/write windows use PAGE_SIZE; standard FAT and cache diagnostic extent guard unchanged. No root-directory repair or timing change.'
for label in old['trees']:
 dst=B/label;subprocess.run(['git','init','-q',str(dst)],check=True);subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True)
 subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True);r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c')
r['loader_fat_unchanged_sha256']=sha(B/'reactos/boot/freeldr/freeldr/lib/fs/fat.c')
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'837',b'838')
 (K/n).write_bytes(data)
for n in ['cache838.c','cache838.h']:(K/n).write_bytes((B/'fatx'/fd/n).read_bytes())
for n in ['build-chain002.py','build-driver002.py','qualify-chain.py','host006.py','cpu005.py','build001.py','qualify-driver002.py','review-driver.py','physical.py']:
 t=(A/n).read_text().replace('boot720-cache837','boot720-fatpage838').replace('837','838').replace('source002.json','source001.json')
 if n=='physical.py':t=t.replace("['driver002'","['fatpage001','driver002'").replace('isolated FATX cache diagnostic838','isolated FATX metadata page fix838 with cache diagnostic')
 (K/n).write_text(t)
base=json.loads((A/'baseline001.json').read_text());audit=json.loads((A/'audit001.json').read_text())
assert audit['completed'] and all(v['matches_baseline'] for v in audit['critical'].values())
base['scope']='Installed baseline unchanged after837; immutable archive support and isolated838 driver. No runtime parent.'
base['projected_console_reserve']['additional_owned_budget']+=16*1024**2
base['projected_console_reserve']['projected_remaining']-=16*1024**2
(K/'baseline001.json').write_text(json.dumps(base,indent=2)+'\n')
(K/'.gitattributes').write_bytes(b'* -text\n')
print('838 fresh source prepared; FATX page windows; unchanged720p')
