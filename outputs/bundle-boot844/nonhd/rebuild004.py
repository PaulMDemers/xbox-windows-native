from pathlib import Path
import os,sys,json,subprocess,hashlib,shutil,shlex,datetime
K=Path(__file__).resolve().parent; W=K.parents[2]; B=Path(os.environ['XWN_BUILD_DIR']); O=Path(os.environ['XWN_OUTPUT_DIR']); P=Path(os.environ['XWN_REPLAY_SOURCE']); C=Path(os.environ['XWN_CROMWELL_SOURCE']); R=Path(os.environ['XWN_ROSBE'])
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists() and not O.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();run=lambda a,**kw:subprocess.run(a,check=True,**kw)
r={'status':'started','physical_access':False,'guest_launch':False,'space':require_space(B,23),'commands':[],'source_only':True}
B.mkdir();O.mkdir(parents=True)
def save(): (O/'build-report.json').write_text(json.dumps(r,indent=2)+'\n')
def call(a,**kw):r['commands'].append([str(x) for x in a]);save();return run(a,**kw)
save()
try:
 lock=json.loads((W/'outputs/video-trace-reuse/inputs.json').read_text()); record=json.loads((P.parent/'build-report.json').read_text());assert record['status']=='compiled' and record['verified_source_tree']==lock['result_tree'];assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()==lock['result_tree'];assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 for n,h in lock['tool_sha256'].items():assert sha(R/n)==h
 ros=B/'reactos';ros.mkdir();call(['git','-C',str(P),'checkout-index','--all','--prefix='+str(ros)+'/']);call(['git','init','-q',str(ros)]);call(['git','-C',str(ros),'add','-f','.']);assert subprocess.check_output(['git','-C',str(ros),'write-tree'],text=True).strip()==lock['result_tree']
 patch=W/'outputs/stock-boot334/reactos.patch';r['e_patch_sha256']=sha(patch);call(['git','-C',str(ros),'apply','--index',str(patch)]);f=ros/'boot/freeldr/freeldr/lib/fs/fat.c'; before=f.read_bytes(); fixed=Path(os.environ['XWN_FIXED_FAT_SOURCE']).read_bytes(); assert hashlib.sha256(fixed).hexdigest()=='d6abab83f78eb81951e9887b43eabf3dacbc768295a5745db6cc471a95fba9df';f.write_bytes(fixed);call(['git','-C',str(ros),'add',str(f)]);r['root_fat_before_sha256']=hashlib.sha256(before).hexdigest();r['root_fat_after_sha256']=hashlib.sha256(fixed).hexdigest();r['reactos_tree']=subprocess.check_output(['git','-C',str(ros),'write-tree'],text=True).strip()
 assert subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip()=='9fc54d0c7cbed7bc3c70373642d833684853011f'
 crom=B/'cromwell';crom.mkdir();archive=subprocess.Popen(['git','-C',str(C),'archive','HEAD'],stdout=subprocess.PIPE);call(['tar','-x','-C',str(crom)],stdin=archive.stdout);archive.stdout.close();assert archive.wait()==0
 old=W/'outputs/native-windows-physical-loader';launch=json.loads((W/'outputs/native-windows-physical-f/launcher.json').read_text());p1=(old/'cromwell-base.patch').read_bytes();p2=(old/'cromwell-fatx-preflight.patch').read_bytes().replace(b'XWNLoader',b'XWNFBoot');assert hashlib.sha256(p1).hexdigest()==launch['base_patch_sha256'];assert hashlib.sha256(p2).hexdigest()==launch['patch_sha256']
 for p in [p1,p2]:call(['patch','-p1'],cwd=crom,input=p,stdout=subprocess.DEVNULL)
 f=crom/'boot/BootResetAction.c';before=f.read_bytes();assert before.count(b'XWNFBoot')==2;f.write_bytes(before.replace(b'XWNFBoot',b'XWNEBoot'));r['cromwell_path_before']=hashlib.sha256(before).hexdigest();r['cromwell_path_after']=sha(f)
 v=crom/'drivers/video/BootVgaInitialization.c'; text=v.read_text(); before=text
 guard='\tav_type = DetectAvType();\n\tgpu.av_type = av_type;'
 hardened='\tav_type = DetectAvType();\n\tif (av_type != AV_COMPOSITE && av_type != AV_SVIDEO && av_type != AV_SCART_RGB) {\n\t\t__asm__ __volatile__(\"cli\"); for (;;) __asm__ __volatile__(\"hlt\");\n\t}\n\tgpu.av_type = av_type;'
 assert text.count(guard)==1;text=text.replace(guard,hardened)
 f=crom/'boot/BootResetAction.c';bt=f.read_text();anchor='\tBootDetectMemorySize();';assert bt.count(anchor)==1
 bt=bt.replace(anchor,anchor+'\n\tif (xbox_ram != 64) { __asm__ __volatile__(\"cli\"); for (;;) __asm__ __volatile__(\"hlt\"); }');f.write_text(bt)

 old="""	} else { // 4:3 TV
		pvmode->m_nVideoModeIndex=VIDEO_PREFERRED_MODE;
	}"""
 new="""	} else { // Fixed profile: refuse before scanout or encoder programming.
		__asm__ __volatile__("cli"); for (;;) __asm__ __volatile__("hlt");
	}"""
 assert text.count(old)==1;text=text.replace(old,new);v.write_text(text)
 import difflib
 (O/'mode-guard.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),text.splitlines(True),'a/drivers/video/BootVgaInitialization.c','b/drivers/video/BootVgaInitialization.c')))
 r['guard_source_before']=hashlib.sha256(before.encode()).hexdigest();r['guard_source_after']=sha(v)
 call(['git','init','-q',str(crom)]);call(['git','-C',str(crom),'add','-f','.']);r['cromwell_tree']=subprocess.check_output(['git','-C',str(crom),'write-tree'],text=True).strip()
 cc=Path('/usr/bin/gcc-12');assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4';r['gcc_sha256']=sha(cc)
 defs=dict(lock['profiles']['video']['definitions']);defs.update(XBOX_NATIVE_FATX_F_BOOT='OFF',XBOX_NATIVE_EXTENDED_NT5_BOOT='OFF',XBOX_NATIVE_FATX_E_BOOT='ON');r['definitions']=defs
 build=B/'nt5';configure=['cmake','-S',str(ros),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(ros/'toolchain-gcc.cmake')]+['-D'+k+'='+v for k,v in defs.items()];compile=['cmake','--build',str(build),'--target','freeldr','rosload','--','-j4'];script='set -e\n'+shlex.join(configure)+'\n'+shlex.join(compile)+'\n';(O/'commands.sh').write_text(script)
 with (O/'nt5.log').open('w') as log:call([str(R/'RosBE.sh'),str(ros),'0','i386'],input=script,text=True,stdout=log,stderr=log,timeout=900)
 for p,n in [('boot/freeldr/freeldr/freeldr.sys','freeldr.sys'),('boot/freeldr/freeldr/rosload.exe','rosload.exe')]:shutil.copyfile(build/p,O/n)
 host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec /usr/bin/gcc-12 "$@"\n');(host/'gcc').chmod(0o755);env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH']);args=['make','all','CC=/usr/bin/gcc-12','GITREV=9fc54d0-xwn-eboot','EXTRA_CROM_CFLAGS=-DXWN_PHYSICAL_PREFLIGHT']
 with (O/'cromwell.log').open('w') as log:call(args,cwd=crom,env=env,stdout=log,stderr=log,timeout=300)
 for p,n in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(crom/p,O/n)
 r['status']='compiled'
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()};r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
