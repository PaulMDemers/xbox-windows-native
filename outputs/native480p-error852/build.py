from pathlib import Path
import os,sys,subprocess,hashlib,json,shutil,difflib
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/home/paul/xbox-windows-native/build/native480p633-build001/source');B=Path('/home/paul/xbox-windows-native/build/native480p-error852/source');O=Path('/mnt/d/xwn852/build001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists() and not O.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
space=require_space(B.parent,20.125)
run=lambda args,**kw:subprocess.run(args,check=True,**kw)
assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()=='70c0a6c5aff82537f489e7d18410d5980fa797a7'
assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
B.mkdir(parents=True);O.mkdir(parents=True);run(['git','-C',str(P),'checkout-index','--all','--prefix='+str(B)+'/'])
changes={};patch=[]
def edit(path,changeset):
 f=B/path;before=f.read_text();after=before
 for old,new in changeset:
  assert after.count(old)==1,(path,old);after=after.replace(old,new)
 f.write_text(after);changes[path]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/'+path,'b/'+path))
edit('drivers/video/xwn_hd_adapter.c',[(' s->stage=1;s->vpll=io->r32(O,0x680508);', ' extern volatile unsigned XwnFailStage852, XwnDetail852;\n s->stage=1;s->vpll=io->r32(O,0x680508);'), (' if(io->r32(O,0x680838)!=p.width-1', ' XwnDetail852=21;\n if(io->r32(O,0x680838)!=p.width-1'), (' io->w8(O,0x6013d4,0x13);', ' XwnDetail852=22;\n io->w8(O,0x6013d4,0x13);'), (' io->w8(O,0x6013d4,0x19);', ' XwnDetail852=23;\n io->w8(O,0x6013d4,0x19);'), (' io->w8(O,0x6013d4,0x28);', ' XwnDetail852=24;\n io->w8(O,0x6013d4,0x28);'), (' io->out8(O,0x80d3,5);s->stage=255;return -1;', ' XwnFailStage852=s->stage; if(s->error>=11 && s->error<=13)XwnDetail852=s->smb_attempts;\n io->out8(O,0x80d3,5);s->stage=255;return -1;')])
edit('drivers/video/xwn_hd_native.c',[('int XwnHdTry720(CURRENT_VIDEO_MODE_DETAILS *mode,unsigned encoder,unsigned cable,unsigned flags){', 'volatile unsigned XwnFailStage852, XwnDetail852;\nstatic void halt852(void){__asm__ __volatile__("cli" ::: "memory");for(;;)__asm__ __volatile__("hlt");}\nstatic void sleep852(unsigned ms){unsigned i;for(i=0;i<ms;i++)hd_delay(0,1000);}\nstatic void led852(const struct xwn_hd_io *io,unsigned mask){if(xwn_hd_smb_write(io,0x10,8,mask))halt852();}\nstatic void group852(const struct xwn_hd_io *io,unsigned color,unsigned count){unsigned i;for(i=0;i<count;i++){led852(io,color);sleep852(500);led852(io,0);sleep852(500);}sleep852(2000);}\nstatic void report852(const struct xwn_hd_io *io,unsigned stage,unsigned error,unsigned detail){\n if(stage>4 || error>30 || detail>24)halt852();\n if(xwn_hd_smb_write(io,0x10,8,0)||xwn_hd_smb_write(io,0x10,7,1))halt852();\n for(;;){sleep852(4000);group852(io,0xff,stage+1);group852(io,0xf0,error/10+1);group852(io,0x0f,error%10+1);group852(io,0xf0,detail/10+1);group852(io,0x0f,detail%10+1);}\n}\nint XwnHdTry720(CURRENT_VIDEO_MODE_DETAILS *mode,unsigned encoder,unsigned cable,unsigned flags){'), ('  (void)xwn_hd_smb_write(&io,0x10,0x02,0x01);', '  __asm__ __volatile__("cli" ::: "memory"); report852(&io,XwnFailStage852,XwnHdState311.error,XwnDetail852);')])
(K/'error852.patch').write_text(''.join(patch));cc=Path('/usr/bin/gcc-12');assert hashlib.sha256(cc.read_bytes()).hexdigest()=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec /usr/bin/gcc-12 "$@"\n');(host/'gcc').chmod(0o755)
flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_720P=1 -DXWN_HD_BOOT_MODE=3';args=['make','all','CC=/usr/bin/gcc-12','GITREV=xwn852-error','EXTRA_CROM_CFLAGS='+flags]
r={'passed':False,'parent_tree':'70c0a6c5aff82537f489e7d18410d5980fa797a7','changes':changes,'space':space,'flags':flags,'physical_access':False,'guest_launch':False}
try:
 with (O/'build.log').open('w') as log:run(args,cwd=B,env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH']),stdout=log,stderr=log,timeout=300)
 for src,name in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(B/src,O/name)
 r['passed']=True
finally:
 r['artifacts']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file()};(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
print('build',r['passed'])
