"""Unique matched Cromwell builds; copies parent index, never edits it/deploys."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
parent=pathlib.Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001/cromwell')
base=pathlib.Path('/home/paul/xbox-windows-native/build/hd-loader311-build001')
out=pathlib.Path('/mnt/d/xwn311/build001')
assert not base.exists() and not out.exists() and not (K/'build001.json').exists()
space=require_space(parent);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tree=subprocess.check_output(['git','-C',str(parent),'write-tree'],text=True).strip()
assert tree=='a2942021cdd24fb2d60bc1be3b54efd7b01a76c6'
assert not subprocess.check_output(['git','-C',str(parent),'diff','--name-only'])
host=json.loads((K/'host002.json').read_text());assert host['passed']
for n in ['adapter.c','adapter.h','host.c','native.c']:assert sha(K/n)==host['source'][n]
cc=pathlib.Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
base.mkdir();out.mkdir(parents=True)
r=dict(status='preparing',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,parent_tree=tree,compiler_sha256=sha(cc),cases={},commands=[])
def record(): (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
def run(args,log,**kw):
 r['commands'].append(list(map(str,args)));return subprocess.run(args,check=True,stdout=log,stderr=log,**kw)
def change(root,name,old,new):
 p=root/name;t=p.read_text();assert t.count(old)==1,(name,old);p.write_text(t.replace(old,new))
try:
 source=base/'source';source.mkdir()
 subprocess.run(['git','-C',str(parent),'checkout-index','--all','--prefix='+str(source)+'/'],check=True)
 original={n:sha(source/n) for n in ['Makefile','drivers/video/Makefile','drivers/video/BootVgaInitialization.c']}
 for n in ['profile.c','profile.h']:
  t=(K.parent/'hd-profile310'/n).read_text()
  t=t.replace('"profile.h"','"xwn_hd_profile.h"').replace('#include <stddef.h>\n','')
  if n.endswith('.c'):t='#ifdef XWN_HD_TIMING_720P\n'+t+'\n#endif\n'
  (source/'drivers/video'/('xwn_hd_'+n)).write_text(t)
 for n in ['adapter.c','adapter.h','native.c']:
  t=(K/n).read_text().replace('"profile.h"','"xwn_hd_profile.h"').replace('"adapter.h"','"xwn_hd_adapter.h"')
  if n=='adapter.c':t='#ifdef XWN_HD_TIMING_720P\n'+t+'\n#endif\n'
  (source/'drivers/video'/('xwn_hd_'+n)).write_text(t)
 change(source,'Makefile','OBJECTS-CROM += $(TOPDIR)/obj/VideoInitialization.o','OBJECTS-CROM += $(TOPDIR)/obj/VideoInitialization.o\nOBJECTS-CROM += $(TOPDIR)/obj/xwn_hd_profile.o $(TOPDIR)/obj/xwn_hd_adapter.o $(TOPDIR)/obj/xwn_hd_native.o')
 change(source,'drivers/video/Makefile','O_TARGET := conexant.o','O_TARGET := xwn_hd_profile.o xwn_hd_adapter.o xwn_hd_native.o conexant.o')
 change(source,'drivers/video/BootVgaInitialization.c','unsigned int video_encoder;','#ifdef XWN_HD_TIMING_720P\nextern int XwnHdTry720(CURRENT_VIDEO_MODE_DETAILS *,unsigned,unsigned,unsigned);\n#endif\n\nunsigned int video_encoder;')
 anchor='\tmapNvMem(&riva,pvmode->m_pbBaseAddressVideo);'
 hook='''#ifdef XWN_HD_TIMING_720P
	if (XwnHdTry720(pvmode,video_encoder,av_type,((u8 *)&eeprom)[0x96])) {
		mapNvMem(&riva,pvmode->m_pbBaseAddressVideo);
		NVVertIntrEnabled(&riva,0);
		NVSetFBStart(&riva,0,pvmode->m_dwFrameBufferStart);
		return;
	}
#endif

'''
 change(source,'drivers/video/BootVgaInitialization.c',anchor,hook+anchor)
 changes={n:dict(before=h,after=sha(source/n)) for n,h in original.items()}
 additions={str(p.relative_to(source)):sha(p) for p in (source/'drivers/video').glob('xwn_hd_*')}
 r['source_changes']=changes;r['source_additions']=additions
 subprocess.run(['git','init','-q',str(source)],check=True)
 subprocess.run(['git','-C',str(source),'add','-f','.'],check=True)
 r['source_tree']=subprocess.check_output(['git','-C',str(source),'write-tree'],text=True).strip()
 (K/'source-review001.json').write_text(json.dumps(dict(parent_tree=tree,tree=r['source_tree'],changes=changes,additions=additions,profile_transform='Rename include, omit unused stddef include, opt-in wrapper only',adapter_transform='Rename includes and opt-in wrapper only',passed=True),indent=2)+'\n')
 record()
 hostbin=out/'host';hostbin.mkdir();(hostbin/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(hostbin/'gcc').chmod(0o755)
 env=dict(os.environ,PATH=str(hostbin)+':'+os.environ['PATH'])
 for name,enabled in [('control001',False),('candidate001',True)]:
  require_space(base);root=base/name;root.mkdir();dest=out/name;dest.mkdir()
  with (out/(name+'.log')).open('w') as log:
   run(['git','-C',str(source),'checkout-index','--all','--prefix='+str(root)+'/'],log)
   flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1'+(' -DXWN_HD_TIMING_720P=1' if enabled else '')
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
