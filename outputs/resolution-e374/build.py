"""Fresh E-path 720p launcher from the qualified 311 source, under build lease."""
import datetime,difflib,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/build/hd-loader311-build001/source')
B=Path('/home/paul/xbox-windows-native/build/resolution-e374-build001/source')
O=Path('/mnt/e/xwn374/build001')
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not O.exists() and not (K/'build001.json').exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(B.parent)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()=='0c91ebed7809d186f328c0b8cc30f612df0cfc7d'
assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
B.mkdir(parents=True);O.mkdir(parents=True)
subprocess.run(['git','-C',str(P),'checkout-index','--all','--prefix='+str(B)+'/'],check=True)
p=B/'boot/BootResetAction.c';before=p.read_text();assert before.count('XWNFBoot')==2
after=before.replace('XWNFBoot','XWNEBoot');p.write_text(after)
(K/'cromwell.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/boot/BootResetAction.c','b/boot/BootResetAction.c')))
subprocess.run(['git','init','-q',str(B)],check=True);subprocess.run(['git','-C',str(B),'add','-f','.'],check=True)
tree=subprocess.check_output(['git','-C',str(B),'write-tree'],text=True).strip()
cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_720P=1'
args=['make','all','CC='+str(cc),'GITREV=9fc54d0-xwn-eboot','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(B/'scripts/ldscript-crom.ld')+' -Map='+str(O/'image-crom.map')]
r=dict(status='building',parent=str(P),parent_tree='0c91ebed7809d186f328c0b8cc30f612df0cfc7d',tree=tree,change='Only two XWNFBoot strings become XWNEBoot',space=space,flags=flags,command=args,gcc12_sha256=sha(cc),physical_access=False,guest_launch=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    with (O/'cromwell.log').open('w') as log:subprocess.run(args,cwd=B,env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH']),stdout=log,stderr=log,check=True,timeout=300)
    for rel,name in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/image-crom.bin','image-crom.bin')]:shutil.copyfile(B/rel,O/name)
    r['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};r['status']='compiled'
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:save()
