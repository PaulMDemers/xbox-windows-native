"""Fresh explicit480p E-path loader. Build only; never installs or launches."""
import datetime,difflib,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
P=Path('/home/paul/xbox-windows-native/build/resolution-e374-build001/source')
B=Path('/home/paul/xbox-windows-native/build/native480p633-build001/source')
O=Path('/mnt/c/xwn633/build001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not O.exists() and not (K/'build001.json').exists()
assert json.loads((K/'host001.json').read_text())['passed']
assert json.loads((K.parent/'mode-facts632/physical-final001.json').read_text())['physical_fact_probe_passed']
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
space=require_space(B.parent,minimum_gib=20.125)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()=='0a1b542e92c8697422892c9cfaed633a5aed0de7'
assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
B.mkdir(parents=True);O.mkdir(parents=True)
subprocess.run(['git','-C',str(P),'checkout-index','--all','--prefix='+str(B)+'/'],check=True)
changes={};patch=[]
for name in ('xwn_hd_profile.c','xwn_hd_profile.h','xwn_hd_adapter.c','xwn_hd_adapter.h','xwn_hd_native.c'):
 target=B/'drivers/video'/name;before=target.read_bytes();after=(K/name).read_bytes()
 assert after==(K.parents[1]/'src/boot/xromwell/drivers/video'/name).read_bytes()
 target.write_bytes(after)
 if before!=after:
  changes[str(target.relative_to(B))]=dict(before=hashlib.sha256(before).hexdigest(),after=sha(target))
  patch.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),'a/drivers/video/'+name,'b/drivers/video/'+name))
assert len(changes)==4
(K/'cromwell.patch').write_text(''.join(patch))
subprocess.run(['git','init','-q',str(B)],check=True);subprocess.run(['git','-C',str(B),'add','-f','.'],check=True)
tree=subprocess.check_output(['git','-C',str(B),'write-tree'],text=True).strip()
cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_720P=1 -DXWN_HD_BOOT_MODE=3'
args=['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(B/'scripts/ldscript-crom.ld')+' -Map='+str(O/'image-crom.map')]
r=dict(status='building',parent=str(P),parent_tree='0a1b542e92c8697422892c9cfaed633a5aed0de7',tree=tree,source=str(B),changes=changes,space=space,flags=flags,command=args,gcc12_sha256=sha(cc),physical_access=False,guest_launch=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 with (O/'cromwell.log').open('w') as log:subprocess.run(args,cwd=B,env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH']),stdout=log,stderr=log,check=True,timeout=300)
 for rel,name in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/image-crom.bin','image-crom.bin')]:shutil.copyfile(B/rel,O/name)
 r['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};r['status']='compiled'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(status=r['status'],xbe=r['outputs']['default.xbe'])))
