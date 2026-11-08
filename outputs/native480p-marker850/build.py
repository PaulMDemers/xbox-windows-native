from pathlib import Path
import os,sys,subprocess,hashlib,json,shutil,difflib
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/home/paul/xbox-windows-native/build/native480p633-build001/source');B=Path('/home/paul/xbox-windows-native/build/native480p-marker850-002/source');O=Path('/mnt/d/xwn850/build002')
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
edit('boot/BootResetAction.c',[("\tBootEepromReadEntireEEPROM();","\tBootEepromReadEntireEEPROM();\n\textern void XwnMarker850(unsigned);\n\tXwnMarker850(0x05); /* early native: PCI, RAM and EEPROM initialized */"),("        BootFromDevice(&entry);","        XwnMarker850(0xa5); /* dispatch: about to call loader */\n        BootFromDevice(&entry);")])
edit('drivers/video/xwn_hd_adapter.c',[(" s->stage=1;s->vpll=io->r32(O,0x680508);"," extern void XwnMarker850(unsigned); XwnMarker850(0x0f); /* guard passed */\n s->stage=1;s->vpll=io->r32(O,0x680508);")])
edit('drivers/video/xwn_hd_native.c',[("int XwnHdTry720(CURRENT_VIDEO_MODE_DETAILS *mode,unsigned encoder,unsigned cable,unsigned flags){",'''/* Bounded transfers, but peripheral and timer failures have no wall-clock guarantee. */
void XwnMarker850(unsigned pattern){
 const struct xwn_hd_io io={0,hd_r32,hd_w32,hd_r8,hd_w8,hd_in16,hd_in8,hd_out16,hd_out8,hd_delay};
 unsigned i;
 if(xwn_hd_smb_write(&io,0x10,0x08,pattern) || xwn_hd_smb_write(&io,0x10,0x07,1)) return;
 for(i=0;i<3000;i++) hd_delay(0,1000);
}
int XwnHdTry720(CURRENT_VIDEO_MODE_DETAILS *mode,unsigned encoder,unsigned cable,unsigned flags){'''),(" int result=xwn_hd_apply(&io,&r,&XwnHdState311);"," XwnMarker850(0xf0); /* guard invocation */\n int result=xwn_hd_apply(&io,&r,&XwnHdState311);"),("  /* Partial display setup cannot fall through into Windows or legacy setup.\n   * Request the same quick reset as the existing SMC helper, with a bounded\n   * transaction. If hardware does not reset, halt with state retained. */","  /* Diagnostic: retain a terminal marker and halt; manual recovery required. */"),("  (void)xwn_hd_smb_write(&io,0x10,0x02,0x01);","  XwnMarker850(result==0 ? 0x50 : 0xf5); /* hold at guard or transaction failure */"),(" if(result==1 && xwn_hd_get_profile(XWN_HD_BOOT_MODE,&selected)){"," if(result==1) XwnMarker850(0xff); /* display transaction completed */\n if(result==1 && xwn_hd_get_profile(XWN_HD_BOOT_MODE,&selected)){")])
(K/'marker850-002.patch').write_text(''.join(patch));cc=Path('/usr/bin/gcc-12');assert hashlib.sha256(cc.read_bytes()).hexdigest()=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec /usr/bin/gcc-12 "$@"\n');(host/'gcc').chmod(0o755)
flags='-DXWN_PHYSICAL_PREFLIGHT -DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_720P=1 -DXWN_HD_BOOT_MODE=3';args=['make','all','CC=/usr/bin/gcc-12','GITREV=xwn850-marker','EXTRA_CROM_CFLAGS='+flags]
r={'passed':False,'parent_tree':'70c0a6c5aff82537f489e7d18410d5980fa797a7','changes':changes,'space':space,'flags':flags,'physical_access':False,'guest_launch':False}
try:
 with (O/'build.log').open('w') as log:run(args,cwd=B,env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH']),stdout=log,stderr=log,timeout=300)
 for src,name in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(B/src,O/name)
 r['passed']=True
finally:
 r['artifacts']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.iterdir() if p.is_file()};(K/'build002.json').write_text(json.dumps(r,indent=2)+'\n')
print('build',r['passed'])
