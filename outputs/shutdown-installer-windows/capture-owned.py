"""One unpaused framebuffer read of the owned observer experiment only."""
import datetime,hashlib,json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
from PIL import Image
run=ws/'work/runs/nt5-shutdown-installer-windows-001'
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
out=k/'001';report=out/'screen-observation.json';assert not report.exists()
r=dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       physical_access=False,paused=False,guest_writes=False,port=4594)
lock=acquire_monitor_lock(4594)
try:
    reply=command(4594,'xp /1wx 0xfd600800');r['framebuffer_query']=reply
    match=re.findall(r'fd600800:\s+0x([0-9a-fA-F]+)',reply);assert match
    address=int(match[-1],16)&0x0fffffff
    width,height,pitch=1024,576,4096;size=height*pitch
    assert address<=0x4000000-size
    raw=out/'artifacts/screen.raw';raw.parent.mkdir(exist_ok=True);assert not raw.exists()
    command(4594,'pmemsave '+str(address)+' '+str(size)+' '+json.dumps(raw.resolve().as_posix()))
    data=raw.read_bytes();assert len(data)==size
    Image.frombytes('RGB',(width,height),data,'raw','BGRX',pitch,1).save(out/'artifacts/screen.png')
    r.update(captured=True,address=hex(address),width=width,height=height,pitch=pitch,raw_sha256=hashlib.sha256(data).hexdigest(),limits='Unpaused memory read can tear and perturb scheduling; fixed known framebuffer geometry.')
except Exception as e:
    r.update(captured=False,error=type(e).__name__,detail=str(e))
finally:
    report.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
