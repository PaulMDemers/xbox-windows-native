"""Fresh exact311720p control and isolated3161080i candidate; no deployment."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
parent=pathlib.Path('/home/paul/xbox-windows-native/build/hd-loader311-build001/source')
base=pathlib.Path('/home/paul/xbox-windows-native/build/hd-interlace316-build001');out=pathlib.Path('/mnt/d/xwn316/build001')
assert not base.exists() and not out.exists() and not (K/'build001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
space=require_space(parent);tree=subprocess.check_output(['git','-C',str(parent),'write-tree'],text=True).strip()
assert tree=='0c91ebed7809d186f328c0b8cc30f612df0cfc7d'
assert not subprocess.check_output(['git','-C',str(parent),'diff','--name-only'])
host=json.loads((K/'host002.json').read_text());assert host['passed']
for n in ['adapter.c','adapter.h','host.c','native.c']:assert sha(K/n)==host['source'][n]
cc=pathlib.Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
base.mkdir();out.mkdir(parents=True)
r=dict(status='preparing',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,parent_tree=tree,compiler_sha256=sha(cc),cases={},commands=[],physical_access=False)
def record():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
def run(args,log,**kw):
 r['commands'].append(list(map(str,args)));return subprocess.run(args,check=True,stdout=log,stderr=log,**kw)
try:
 source=base/'source';source.mkdir();subprocess.run(['git','-C',str(parent),'checkout-index','--all','--prefix='+str(source)+'/'],check=True)
 names=['drivers/video/xwn_hd_profile.c','drivers/video/xwn_hd_adapter.c','drivers/video/xwn_hd_adapter.h','drivers/video/xwn_hd_native.c','drivers/video/BootVgaInitialization.c']
 original={n:sha(source/n) for n in names}
 for n in ['adapter.c','adapter.h','native.c']:
  t=(K/n).read_text().replace('"profile.h"','"xwn_hd_profile.h"').replace('"adapter.h"','"xwn_hd_adapter.h"')
  if n=='adapter.c':t='#ifdef XWN_HD_TIMING_1080I\n'+t+'\n#endif\n'
  (source/'drivers/video'/('xwn_hd_'+n)).write_text(t)
 p=source/'drivers/video/xwn_hd_profile.c';p.write_text(p.read_text().replace('XWN_HD_TIMING_720P','XWN_HD_TIMING_1080I'))
 p=source/'drivers/video/BootVgaInitialization.c';t=p.read_text();assert t.count('XwnHdTry720')==2 and t.count('XWN_HD_TIMING_720P')==2;p.write_text(t.replace('XwnHdTry720','XwnHdTry1080').replace('XWN_HD_TIMING_720P','XWN_HD_TIMING_1080I'))
 r['source_changes']={n:dict(before=h,after=sha(source/n)) for n,h in original.items()}
 subprocess.run(['git','init','-q',str(source)],check=True);subprocess.run(['git','-C',str(source),'add','-f','.'],check=True)
 r['source_tree']=subprocess.check_output(['git','-C',str(source),'write-tree'],text=True).strip();record()
 hostbin=out/'host';hostbin.mkdir();(hostbin/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(hostbin/'gcc').chmod(0o755)
 env=dict(os.environ,PATH=str(hostbin)+':'+os.environ['PATH'])
 for name,origin,mode in [('control001',parent,'720P'),('candidate001',source,'1080I')]:
  require_space(base);root=base/name;root.mkdir();dest=out/name;dest.mkdir()
  with (out/(name+'.log')).open('w') as log:
   run(['git','-C',str(origin),'checkout-index','--all','--prefix='+str(root)+'/'],log)
   flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_'+mode+'=1'
   args=['make','all','CC='+str(cc),'GITREV=9fc54d0-xwn-fboot','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(root/'scripts/ldscript-crom.ld')+' -Map='+str(dest/'image-crom.map')]
   run(args,log,cwd=root,env=env)
   files={}
   for rel,n in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/xbeboot.elf','xbeboot.elf'),('obj/image-crom.bin','image-crom.bin')]:
    shutil.copyfile(root/rel,dest/n);files[n]=dict(sha256=sha(dest/n),bytes=(dest/n).stat().st_size)
   files['image-crom.map']=dict(sha256=sha(dest/'image-crom.map'),bytes=(dest/'image-crom.map').stat().st_size)
   r['cases'][name]=dict(status='compiled',flags=flags,files=files);record();print(name,'compiled',flush=True)
 r['status']='compiled'
except Exception as e:r.update(status='failed',error=repr(e));raise
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['logs']={p.name:sha(p) for p in out.glob('*.log')};record();print(r['status'],flush=True)
