"""Bounded HMP observation only. No guest memory/register writes or input injection."""
import datetime,json,shutil,sys,time,hashlib,struct,zlib,re
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn636/emu002')
sys.path.insert(0,str(K.parent/'native480p633'));from protocol import monitor
r=dict(physical_access=False,debugger=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),samples=[],captures=[],quit_requested=False)
out=K/'observation002.json';assert not out.exists();start=time.monotonic()
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for i in range(20):
  try:monitor(5668,'info status');break
  except OSError:time.sleep(.5)
 else:raise RuntimeError('Owned monitor not ready')
 while time.monotonic()-start<600:
  elapsed=round(time.monotonic()-start,2);status=monitor(5668,'info status');free=shutil.disk_usage('C:/').free
  disk=(P/'hdd.qcow2').stat().st_size
  r['samples'].append(dict(elapsed=elapsed,status=status.split('VM status:')[-1].splitlines()[0].strip(),c_free=free,disk_bytes=disk));save()
  if free<20*1024**3+48*1024**2:r['stop_reason']='space margin';break
  if disk>128*1024**2:r['stop_reason']='overlay growth bound';break
  if any(p.stat().st_size>16*1024**2 for p in P.glob('*.log')):r['stop_reason']='log growth bound';break
  if 'VM status: running' not in status:r['stop_reason']='guest stopped';break
  if (elapsed>=120 and not r['captures']) or (elapsed>=240 and len(r['captures'])==1):
   label=str(len(r['captures']));row=dict(elapsed=elapsed,scope='Read-only MMIO/RAM capture; BGRX pitch interpretation from candidate')
   for name,addr in [('start',0xfd600800),('width_end',0xfd680838),('height_end',0xfd680818)]:
    reply=monitor(5668,'xp /1wx '+hex(addr));lines=[v for v in reply.splitlines() if re.match(r'^[0-9a-f]{8,16}:',v)];row[name]=int(lines[0].split(':')[1].strip(),16) if len(lines)==1 else None
   if row['start']==0x3700000 and row['width_end']==719 and row['height_end']==479:
    raw=P/('framebuffer'+label+'.bin');row['reply']=monitor(5668,'pmemsave 0x3700000 1382400 "'+raw.as_posix()+'"');data=raw.read_bytes();assert len(data)==1382400
    row['sha256']=hashlib.sha256(data).hexdigest();rows=[]
    for y in range(480):
     line=data[y*2880:(y+1)*2880];rgb=bytearray(2160);rgb[0::3]=line[2::4];rgb[1::3]=line[1::4];rgb[2::3]=line[0::4];rows.append(b'\0'+rgb)
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    (P/('framebuffer'+label+'.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',720,480,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b''))
   r['captures'].append(row);save()
  time.sleep(2)
 else:r['stop_reason']='600second deadline'
except BaseException as e:r['error']=repr(e);raise
finally:
 try:monitor(5668,'quit',True);r['quit_requested']=True
 except OSError as e:r['quit_error']=repr(e)
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
