"""Describe a completed 48 kHz stereo PCM capture and find the diagnostic's 400 Hz periodic tone."""
import argparse,array,hashlib,json,pathlib,sys,wave,math
p=argparse.ArgumentParser();p.add_argument('wave',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
with wave.open(str(a.wave),'rb') as w:
 assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(2,2,48000)
 frames=w.getnframes();data=w.readframes(frames);assert len(data)==frames*4
samples=array.array('h',data)
if sys.byteorder!='little':samples.byteswap()
windows=[];size=4800
for frame in range(0,frames-size+1,size):
 left=samples[frame*2:(frame+size)*2:2];energy=sum(x*x for x in left);rms=math.sqrt(energy/size)
 # A 400 Hz test repeats every 120 samples. This is only a signal fingerprint,
 # not proof of the physical analog output or of the source application.
 diff=sum((left[i]-left[i-120])**2 for i in range(120,size));ratio=math.sqrt(diff/(size-120))/rms if rms else None
 windows.append({'start_seconds':frame/48000,'rms':round(rms,3),'period_error_ratio':round(ratio,5) if ratio is not None else None,'tone_candidate':rms>10 and ratio is not None and ratio<.03})
longest=run=0;segments=[]
for window in windows:
 if window['tone_candidate']:run+=1;longest=max(longest,run)
 elif run:segments.append({'start_seconds':round(window['start_seconds']-run*.1,3),'duration_seconds':round(run*.1,3)});run=0
if run:segments.append({'start_seconds':round(windows[-1]['start_seconds']-(run-1)*.1,3),'duration_seconds':round(run*.1,3)})
report={'scope':__doc__,'sha256':hashlib.sha256(a.wave.read_bytes()).hexdigest(),'frames':frames,'duration_seconds':frames/48000,'peak':max(map(abs,samples),default=0),'longest_400hz_candidate_seconds':longest*.1,'tone_segments':segments,'windows':windows}
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='windows'},indent=2))
