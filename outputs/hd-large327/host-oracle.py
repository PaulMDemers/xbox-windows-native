"""Actual C oracle versus independent forward array copies, never guest evidence."""
import array,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent
out=Path('/mnt/e/xwn327/host001');out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.byteorder=='little'
for n in ['host-oracle.py','host-oracle.c','large_oracle.h']:shutil.copyfile(k/n,out/n)
cc=shutil.which('gcc');assert cc
command=[cc,'-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',str(out/'host-oracle.c'),'-o',str(out/'oracle')]
r=subprocess.run(command,capture_output=True,text=True)
(out/'compile.stdout').write_text(r.stdout);(out/'compile.stderr').write_text(r.stderr)
assert r.returncode==0,r.stderr
env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
def run(*args):
    r=subprocess.run([str(out/'oracle'),*map(str,args)],capture_output=True,env=env,timeout=60)
    assert r.returncode==0 and not r.stderr,(r.returncode,r.stderr)
    return r.stdout
invalid=run().decode().strip();records=[];pixels=0;negatives=0
for w,h in [(256,128),(640,360),(960,540)]:
    cw,ch=w+48,h+48
    # Independent forward byte-pattern construction, not inverse-coordinate recurrence.
    source=array.array('I',((165<<24)|(((17+13*x+3*y)%256)<<16)|(((29+5*x+11*y)%256)<<8)|((43+7*x+19*y)%256) for y in range(ch) for x in range(cw)))
    raw=run(w,h,5,0);assert raw==source.tobytes()
    records.append(dict(size=[w,h],kind='source',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    for kind in range(5):
        for count in [0,1,3,80]:
            expected=array.array('I',(v&0xffffff for v in source))
            for step in range(count):
                if kind==0:
                    row=array.array('I',[0xffffff if step%2==0 else 0])*w
                    for y in range(16,16+h):expected[y*cw+16:y*cw+16+w]=row
                elif kind in (2,3):
                    sx,sy,dx,dy=(16,16,32,32) if kind==2 else (32,32,16,16)
                    # Save complete source before changing any destination row (memmove semantics).
                    copy=[expected[(sy+y)*cw+sx:(sy+y)*cw+sx+w] for y in range(h)]
                    for y,row in enumerate(copy):expected[(dy+y)*cw+dx:(dy+y)*cw+dx+w]=row
                # RAM uploads and repaints copy the unchanged source back to the same coordinates.
            raw=run(w,h,kind,count);wanted=expected.tobytes();assert raw==wanted,(w,h,kind,count)
            pixels+=len(expected)
            for index in [0,15*cw+15,16*cw+16,32*cw+32,len(expected)-1]:
                changed=bytearray(raw);changed[index*4]^=1
                assert changed!=wanted;negatives+=1
            records.append(dict(size=[w,h],kind=kind,count=count,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
result=dict(passed=True,scope='host actual C oracle versus independent forward-copy model; no GDI/guest test',
    command=command,compiler=cc,compiler_sha256=sha(Path(cc)),compiler_version=subprocess.check_output([cc,'--version'],text=True),
    invalid_layouts=6,compared_pixels=pixels,mutated_pixel_or_guard_rejections=negatives,cases=records,
    inputs={n:sha(out/n) for n in ['host-oracle.py','host-oracle.c','large_oracle.h']},binary_sha256=sha(out/'oracle'))
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');(k/'host001.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:result[key] for key in ['passed','invalid_layouts','compared_pixels','mutated_pixel_or_guard_rejections']}))
