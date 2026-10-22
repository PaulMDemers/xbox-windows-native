"""Fresh phase diagnostic from pinned633 source; host validation then build, no deployment."""
import datetime,difflib,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
P=Path('/home/paul/xbox-windows-native/build/native480p633-build001/source')
B=Path('/mnt/c/xwn648/source002'); O=Path('/mnt/c/xwn648/build002')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not O.exists() and not (K/'build002.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='preflight',physical_access=False,guest_launch=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'build002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 # All new sources, objects, host binaries and compiler temp files live on C.
 # No new WSL fixture/disk/source allocation.20MiB margin on both checked volumes.
 r['space']=require_space(O,minimum_gib=20.02)
 assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()=='70c0a6c5aff82537f489e7d18410d5980fa797a7'
 assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 original=(P/'drivers/video/xwn_hd_native.c').read_bytes()
 candidate=(K/'xwn_hd_native.c').read_bytes()
 insertion=(b'\n#include "led648.h"\n#include "trace648.h"\nvolatile unsigned XwnDiag648Status;\n'
 b'static int hd648_send(void *p,unsigned char a,unsigned char r,unsigned char v){return xwn_hd_smb_write((const struct xwn_hd_io *)p,a,r,v);}\n'
 b'static void hd648_delay(void *p,unsigned us){const struct xwn_hd_io *io=p;io->delay(io->opaque,us);}')
 call=b'\n XwnDiag648Status=led648_show((void *)&io,hd648_send,hd648_delay,result,XwnHdState311.stage,XwnHdState311.error,XwnTrace648.failed_wait);'
 assert candidate.count(insertion)==candidate.count(call)==1
 assert candidate.replace(insertion,b'').replace(call,b'')==original
 change=json.loads((K/'source-transform001.json').read_text())
 original_adapter=(P/'drivers/video/xwn_hd_adapter.c').read_text()
 adapter=(K/'xwn_hd_adapter.c').read_text()
 recovered=adapter.replace(change['new_edge'],change['old_edge']).replace(change['insertion'],'').replace(change['init'],'')
 assert recovered==original_adapter
 r['original_native_recovered_exactly']=True
 r['original_adapter_recovered_exactly']=True
 O.mkdir(parents=True); (O/'tmp').mkdir(); B.mkdir(parents=True)
 env=dict(os.environ,TMPDIR=str(O/'tmp'))
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['gcc12_sha256']=sha(cc)
 common=[str(cc),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie','-DXWN_HD_TIMING_720P','-I'+str(K),'-I'+str(P/'drivers/video')]
 commands=[common+['-Dxwn_hd_apply=baseline_apply','-Dxwn_hd_smb_write=baseline_smb_write','-c',str(P/'drivers/video/xwn_hd_adapter.c'),'-o',str(O/'baseline.o')],
           common+[str(K/'adapter-host.c'),str(K/'xwn_hd_adapter.c'),str(P/'drivers/video/xwn_hd_profile.c'),str(O/'baseline.o'),'-o',str(O/'adapter-host')],
           common+[str(K/'led-host.c'),'-o',str(O/'led-host')],
           common+[str(W/'outputs/native480p633/adapter-host.c'),str(K/'xwn_hd_adapter.c'),str(P/'drivers/video/xwn_hd_profile.c'),'-o',str(O/'legacy-host')]]
 r['host_commands']=commands
 for i,args in enumerate(commands):
  x=subprocess.run(args,env=env,capture_output=True,timeout=60);(O/('host-compile'+str(i)+'.txt')).write_bytes(x.stdout+x.stderr);assert x.returncode==0
 r['host']={}
 for name in ['adapter-host','led-host','legacy-host']:
  x=subprocess.run([str(O/name)],env=env,capture_output=True,timeout=90);(O/(name+'-result.txt')).write_bytes(x.stdout+x.stderr);assert x.returncode==0 and not x.stderr
  r['host'][name]={'passed':True,'output':x.stdout.decode(),'hardware_io':'modeled callbacks','binary_sha256':sha(O/name)}
 subprocess.run(['git','-C',str(P),'checkout-index','--all','--prefix='+str(B)+'/'],env=env,check=True,timeout=90)
 (B/'drivers/video/xwn_hd_native.c').write_bytes(candidate)
 for name in ['diag647.h','led648.h','trace648.h','xwn_hd_adapter.c']:(B/'drivers/video'/name).write_bytes((K/name).read_bytes())
 (K/'native002.patch').write_text(''.join(difflib.unified_diff(original.decode().splitlines(True),candidate.decode().splitlines(True),'a/drivers/video/xwn_hd_native.c','b/drivers/video/xwn_hd_native.c')))
 for name in ('xwn_hd_adapter.h','xwn_hd_profile.c','xwn_hd_profile.h'):
  assert (B/'drivers/video'/name).read_bytes()==(P/'drivers/video'/name).read_bytes()
 subprocess.run(['git','init','-q',str(B)],env=env,check=True)
 subprocess.run(['git','-C',str(B),'add','-f','.'],env=env,check=True)
 (K/'adapter002.patch').write_text(''.join(difflib.unified_diff(original_adapter.splitlines(True),adapter.splitlines(True),'a/drivers/video/xwn_hd_adapter.c','b/drivers/video/xwn_hd_adapter.c')))
 r.update(parent_tree='70c0a6c5aff82537f489e7d18410d5980fa797a7',tree=subprocess.check_output(['git','-C',str(B),'write-tree'],text=True).strip(),source=str(B),status='building')
 host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
 flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_720P=1 -DXWN_HD_BOOT_MODE=3'
 args=['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(B/'scripts/ldscript-crom.ld')+' -Map='+str(O/'image-crom.map')]
 r.update(flags=flags,command=args,source_pins={p.name:sha(p) for p in K.iterdir() if p.suffix in ('.py','.c','.h','.patch')});save()
 with (O/'cromwell.log').open('w') as log:subprocess.run(args,cwd=B,env=dict(env,PATH=str(host)+':'+env['PATH']),stdout=log,stderr=log,check=True,timeout=300)
 for src,dst in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/image-crom.bin','image-crom.bin')]:shutil.copyfile(B/src,O/dst)
 r['outputs']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};r['status']='compiled'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(status=r['status'],host=r['host'],xbe=r['outputs']['default.xbe'])))
