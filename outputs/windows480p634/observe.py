"""Bounded HMP observation only. No guest memory/register writes or input injection."""
import datetime,json,shutil,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn634/emu001')
sys.path.insert(0,str(K.parent/'native480p633'));from protocol import monitor
r=dict(physical_access=False,debugger=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),samples=[],captures=[],quit_requested=False)
out=K/'observation001.json';assert not out.exists();start=time.monotonic()
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for i in range(20):
  try:monitor(5648,'info status');break
  except OSError:time.sleep(.5)
 else:raise RuntimeError('Owned monitor not ready')
 while time.monotonic()-start<600:
  elapsed=round(time.monotonic()-start,2);status=monitor(5648,'info status');free=shutil.disk_usage('C:/').free
  disk=(P/'hdd.qcow2').stat().st_size
  r['samples'].append(dict(elapsed=elapsed,status=status.split('VM status:')[-1].splitlines()[0].strip(),c_free=free,disk_bytes=disk));save()
  if free<20*1024**3+48*1024**2:r['stop_reason']='space margin';break
  if disk>128*1024**2:r['stop_reason']='overlay growth bound';break
  if any(p.stat().st_size>16*1024**2 for p in P.glob('*.log')):r['stop_reason']='log growth bound';break
  if 'VM status: running' not in status:r['stop_reason']='guest stopped';break
  if (elapsed>=60 and not r['captures']) or (elapsed>=240 and len(r['captures'])==1):
   p=P/('screen'+str(len(r['captures']))+'.ppm');reply=monitor(5648,'screendump "'+p.as_posix()+'"');r['captures'].append(dict(path=str(p),reply=reply,elapsed=elapsed));save()
  time.sleep(2)
 else:r['stop_reason']='600second deadline'
except BaseException as e:r['error']=repr(e);raise
finally:
 try:monitor(5648,'quit',True);r['quit_requested']=True
 except OSError as e:r['quit_error']=repr(e)
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
