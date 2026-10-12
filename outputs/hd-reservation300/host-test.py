"""Compile actual prepared provider with modeled NT primitives under ASan/UBSan."""
import hashlib,json,pathlib,shutil,subprocess
k=pathlib.Path(__file__).resolve().parent;w=k.parents[1]
src=pathlib.Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001/source')
out=pathlib.Path('/mnt/e/xwn300/host001');assert not out.exists();out.mkdir(parents=True)
pins={}
for p,name in [(src/'drivers/base/bootvid/xwn_fb.c','xwn_fb.c'),(src/'drivers/base/bootvid/xwn_fb.h','xwn_fb.h'),(src/'sdk/include/reactos/drivers/xbox/xwn_hd_layout.h','drivers/xbox/xwn_hd_layout.h'),(w/'outputs/video-shared-framebuffer/tests/ntddk.h','ntddk.h'),(k/'host-test.c','test.c')]:
 q=out/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);pins[name]=hashlib.sha256(q.read_bytes()).hexdigest()
cc=pathlib.Path(shutil.which('gcc')).resolve()
cmd=[str(cc),'-std=c11','-Wall','-Wextra','-Werror','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer','-pthread','-DXBOX_NT5_HD_RESERVATION=1','-DSOURCE_PROVIDER="xwn_fb.c"','-I',str(out),str(out/'test.c'),'-o',str(out/'test')]
r=dict(inputs=pins,compiler=str(cc),compiler_sha256=hashlib.sha256(cc.read_bytes()).hexdigest(),command=cmd,passed=False)
try:
 b=subprocess.run(cmd,capture_output=True,text=True);r['compile']=dict(returncode=b.returncode,stdout=b.stdout,stderr=b.stderr);b.check_returncode()
 b=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);r['test']=dict(returncode=b.returncode,stdout=b.stdout,stderr=b.stderr);b.check_returncode();r['passed']=True
finally:
 r['limits']='NT locks and IRQL are host models. No native mapping, emulator boot, timing or physical qualification.'
 (k/'host001.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
