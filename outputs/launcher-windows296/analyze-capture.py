"""Independently classify captured channels, sequence, duration and silence gaps."""
import array,hashlib,json,math,pathlib,sys,wave
def analyze(path):
 with wave.open(str(path),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(2,2,48000)
  frames=w.getnframes();raw=w.readframes(frames);assert len(raw)==frames*4
 s=array.array('h',raw)
 if sys.byteorder!='little':s.byteswap()
 size=960;windows=[]
 for start in range(0,frames-size+1,size):
  mask=0;valid=True
  for c,period,wrong in [(0,120,80),(1,80,120)]:
   v=s[start*2+c:(start+size)*2:2];rms=math.sqrt(sum(x*x for x in v)/size)
   if rms<=3:continue
   error=lambda p:math.sqrt(sum((v[i]-v[i-p])**2 for i in range(p,size))/(size-p))/rms
   if rms<50 or error(period)>.06 or error(wrong)<.1:valid=False
   else:mask|=1<<c
  windows.append((start/48000,mask if valid else -1))
 segments=[];first=None;current=None
 for t,mask in windows+[(frames/48000,0)]:
  if mask!=current:
   if current in [1,2,3] and first is not None:segments.append({'mask':current,'start':first,'duration':round(t-first,3)})
   first=t;current=mask
 full=[v for v in segments if v['duration']>=1.5]
 expected=[1,2,3,1,2,3]
 sequence=[v['mask'] for v in full]
 durations=all(1.8<=v['duration']<=2.1 for v in full)
 gaps=[]
 for a,b in zip(full,full[1:]):
  begin=a['start']+a['duration'];end=b['start'];inner=[mask for t,mask in windows if begin+.06<=t<end-.06]
  gaps.append({'seconds':round(end-begin,3),'silence_verified':len(inner)>=40 and all(mask==0 for mask in inner)})
 passed=sequence==expected and durations and all(.8<=g['seconds']<=2.0 and g['silence_verified'] for g in gaps)
 return {'passed':passed,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'frames':frames,'segments':segments,'sequence':sequence,'durations_valid':durations,'gaps':gaps,'physical_audibility':False,'scope':__doc__}
if __name__=='__main__':
 p=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);assert not out.exists();r=analyze(p);out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));sys.exit(0 if r['passed'] else 1)
