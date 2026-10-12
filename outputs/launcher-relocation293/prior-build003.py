"""Fresh matched Cromwell relocation builds; never installs or launches."""
import pathlib,subprocess,os,sys,json,hashlib,datetime,shutil
K=pathlib.Path(__file__).resolve().parent;ROOT=K.parents[1]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
mode=sys.argv[1];assert mode in ('control003','candidate003')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=pathlib.Path('/mnt/e/xwn293')/mode
assert not out.exists(),'Never reuse build IDs'
plan=json.loads((K/'source-plan.json').read_text())
assert sha(K/'relocation.patch')==plan['patch_sha256']
cc=pathlib.Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
patches={'outputs/native-windows-physical-loader/cromwell-base.patch':'69964e0a5f5557881486b4668ddd2e940ecbf1cc26110e1960366ca7ecf5e12e','outputs/native-windows-physical-f/cromwell-f-launcher.patch':'1a47d42c371540549a8fb1f4de40404ca8436e4ad35f1e2c8236f82bc367fbb2'}
for n,h in patches.items():assert sha(ROOT/n)==h
out.mkdir(parents=True);src=out/'source';tmp=out/'tmp';tmp.mkdir();host=out/'host-tools';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
r={'mode':mode,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Compilation only; no emulator or hardware launch','inputs':{str(p):sha(p) for p in [K/'build.py',K/'Build.ps1',K/'source-plan.json',K/'relocation.patch']},'compiler_sha256':sha(cc),'patches':patches,'commands':[]}
def run(args,**kw):
 r['commands'].append([str(a) for a in args]);return subprocess.run(args,stdout=log,stderr=log,check=True,**kw)
try:
 with (out/'build.log').open('w') as log:
  run(['git','init','-q',str(src)])
  run(['git','-C',str(src),'fetch','--depth=1','/home/paul/xbox-windows-native/sources/cromwell','9fc54d0c7cbed7bc3c70373642d833684853011f'])
  run(['git','-C',str(src),'checkout','--detach','FETCH_HEAD'])
  for n in patches:run(['git','-C',str(src),'apply',str(ROOT/n)])
  run(['git','-C',str(src),'add','-u'])
  r['base_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip();assert run(['git','-C',str(src),'add','-u'])
  r['base_tree']=='24710a16e07df4c93bbe82d620a0c0a48e3c8097'
  for n,v in plan['files'].items():assert sha(src/n)==v['before_sha256'],n
  if mode=='candidate003':
   run(['git','-C',str(src),'apply',str(K/'relocation.patch')])
   for n,v in plan['files'].items():assert sha(src/n)==v['after_sha256'],n
  run(['git','-C',str(src),'add','-u'])
  r['built_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()
  env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH'],TMPDIR=str(tmp))
  run(['make','all','CC='+str(cc),'GITREV=9fc54d0-xwn-fboot','EXTRA_CROM_CFLAGS=-DXWN_PHYSICAL_PREFLIGHT','LDFLAGS-ROM=-s -S -T '+str(src/'scripts/ldscript-crom.ld')+' -Map='+str(out/'image-crom.map')],cwd=src,env=env)
  for name,p in {'default.xbe':src/'xbe/xromwell.xbe','image-crom.elf':src/'obj/image-crom.elf','image-crom.bin':src/'obj/image-crom.bin','xbeboot.elf':src/'obj/xbeboot.elf'}.items():shutil.copyfile(p,out/name)
  r['artifacts']={n:{'sha256':sha(out/n),'bytes':(out/n).stat().st_size} for n in ['default.xbe','image-crom.elf','image-crom.bin','xbeboot.elf','image-crom.map']}
  r['status']='compiled'
except Exception as e:r.update(status='failed',error=repr(e));raise
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(K/(mode+'.json')).write_text(json.dumps(r,indent=2)+'\n');shutil.copyfile(out/'build.log',K/(mode+'-build.log'));print(json.dumps({'mode':mode,'status':r['status']}))
