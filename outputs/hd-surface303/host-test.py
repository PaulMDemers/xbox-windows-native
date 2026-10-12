"""Actual surface lifecycle code with explicit modeled Eng/miniport interfaces."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;root=Path('/mnt/d/xwn303/host001');dest=k/'host001.json'
assert not root.exists() and not dest.exists();root.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[(k/'host.c','host.c'),(k/'display/surface.c','surface.c'),(k/'surface_bounds.h','surface_bounds.h'),
        (k.parent/'video-ram-ownership/tests/framebuf.h','framebuf.h')]
pins={}
for p,n in inputs:shutil.copyfile(p,root/n);pins[n]=sha(root/n)
cc='/usr/bin/x86_64-linux-gnu-gcc-15';r=dict(passed=False,inputs=pins,compiler_sha256=sha(Path(cc)),cases={})
try:
    for mode in [0,1]:
        args=[cc,'-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',
              '-DXWN_HD_SURFACE_BOUNDS='+str(mode),str(root/'host.c'),'-o',str(root/('test'+str(mode)))]
        c=subprocess.run(args,text=True,capture_output=True);row=dict(command=args,compile=dict(returncode=c.returncode,stdout=c.stdout,stderr=c.stderr));r['cases'][str(mode)]=row
        assert c.returncode==0,c.stderr
        t=subprocess.run([args[-1]],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1'))
        row['test']=dict(returncode=t.returncode,stdout=t.stdout,stderr=t.stderr);assert t.returncode==0,t.stderr
        row['binary_sha256']=sha(Path(args[-1]))
    r['passed']=True
finally:
    r['limits']='Actual DrvEnableSurface/DisableSurface/AssertMode; modeled Eng allocations, upload, device mapping and registry. Not guest drawing, NT5 allocation or physical qualification.'
    dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
