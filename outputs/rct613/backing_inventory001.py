"""Native bounded, resumable QCOW dependency inventory with visible progress."""
import os,time,json,struct,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent
out=K/'backing-inventory001.json'
assert not out.exists()
start=time.monotonic();stack=['/home/paul/xbox-windows-native'];rows=[];count=0;files=0;last=start
r={'completed':False,'directories':0,'files':0,'qcow':[],'pending':stack}
def save():
    r.update(directories=count,files=files,qcow=rows,pending=stack,elapsed_seconds=time.monotonic()-start)
    out.write_text(json.dumps(r,indent=2)+'\n')
try:
    while stack:
        if time.monotonic()-start>180:raise TimeoutError('180-second total budget; pending directories retained')
        d=stack.pop();count+=1
        with os.scandir(d) as entries:
            for e in entries:
                if e.is_dir(follow_symlinks=False):stack.append(e.path)
                elif e.is_file(follow_symlinks=False):
                    files+=1
                    if e.name.endswith('.qcow2'):
                        p=Path(e.path)
                        with p.open('rb') as f:
                            h=f.read(24);assert h[:4]==b'QFI\xfb',e.path
                            offset,length=struct.unpack('>QI',h[8:20]);assert length<4096
                            parent=None
                            if length:
                                assert offset+length<=p.stat().st_size
                                f.seek(offset);back=f.read(length).decode();parent=str((p.parent/back).resolve())
                        rows.append({'path':e.path,'parent':parent})
        if time.monotonic()-last>5:
            save();print(json.dumps({'directories':count,'files':files,'pending':len(stack),'qcow':len(rows)}),flush=True);last=time.monotonic()
    r['completed']=True
except BaseException as e:r['error']=repr(e);raise
finally:save()
print(json.dumps({'completed':True,'directories':count,'files':files,'qcow':len(rows)}))
