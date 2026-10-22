"""New654 source/build only; never launches or reopens a historical runtime."""
import datetime, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/mnt/c/xwn651/source001');S=Path('/mnt/c/xwn654/source001');B=Path('/mnt/c/xwn654/build001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not S.exists() and not (K/'build001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='preflight',physical_access=False,guest_launch=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05)
 parent=json.loads((W/'outputs/readback651/build001.json').read_text())
 assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()==parent['tree']=='2fda813f3b8109dfc6b70f6d37e21d2cf9a66d55'
 assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 B.mkdir(parents=True);S.mkdir(parents=True);(B/'tmp').mkdir()
 env=dict(os.environ,TMPDIR=str(B/'tmp'))
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc)
 r['source_pins']={p.name:sha(p) for p in K.iterdir() if p.suffix in ('.py','.c','.h')}
 def run(name,args,**kwargs):
  r.setdefault('commands',[]).append([str(a) for a in args]);save()
  x=subprocess.run(args,env=env,capture_output=True,timeout=kwargs.pop('timeout',60),**kwargs)
  (B/(name+'.stdout')).write_bytes(x.stdout);(B/(name+'.stderr')).write_bytes(x.stderr)
  assert x.returncode==0,(name,x.returncode)
  return x.stdout.decode()
 run('compile-host',[str(cc),'-std=c99','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(K),'-I'+str(P/'drivers/video'),str(K/'test.c'),'-o',str(B/'test-host')])
 r['host']=json.loads(run('host',[str(B/'test-host')]))
 run('export',['git','-C',str(P),'checkout-index','--all','--prefix='+str(S)+'/'])
 (S/'drivers/video/led651.h').write_bytes((K/'led651.h').read_bytes())
 # Compare every indexed source against the parent. Only the LED header changes.
 paths=subprocess.check_output(['git','-C',str(P),'ls-files','-z']).decode().strip('\0').split('\0')
 changed=[n for n in paths if (S/n).read_bytes()!=(P/n).read_bytes()]
 assert changed==['drivers/video/led651.h'];r['changed_parent_paths']=changed
 run('init',['git','init','-q',str(S)]);run('index',['git','-C',str(S),'add','-f','.'])
 r['tree']=run('tree',['git','-C',str(S),'write-tree']).strip();r['parent_tree']=parent['tree']
 host=B/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
 flags=parent['flags'];r['flags']=flags;env['PATH']=str(host)+':'+env['PATH']
 args=['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(S/'scripts/ldscript-crom.ld')+' -Map='+str(B/'image-crom.map')]
 r['status']='building';save();run('build',args,cwd=S,timeout=300)
 for src,dst in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/image-crom.bin','image-crom.bin')]:shutil.copyfile(S/src,B/dst)
 r['unchanged_object_text']={}
 for rel in ['drivers/video/xwn_hd_adapter.o','drivers/video/xwn_hd_profile.o','lib/misc/BootLibrary.o']:
  # Locate objects from the actual build layout, then compare code sections.
  before=list(P.glob('**/'+Path(rel).name));after=list(S.glob('**/'+Path(rel).name))
  assert len(before)==len(after)==1,(rel,before,after)
  pairs=[]
  for tag,obj in [('before',before[0]),('after',after[0])]:
   dst=B/(Path(rel).stem+'-'+tag+'.text')
   run(Path(rel).stem+'-'+tag,['objcopy','-O','binary','--only-section=.text',str(obj),str(dst)])
   pairs.append(dst.read_bytes())
  assert pairs[0]==pairs[1],rel
  r['unchanged_object_text'][rel]=hashlib.sha256(pairs[0]).hexdigest()
 r['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()}
 r['status']='compiled'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(status=r['status'],host=r['host'],xbe=r['outputs']['default.xbe'])))
