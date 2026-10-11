"""Measure captured emulator PCM independently of waveOut completion reports."""
import array,hashlib,json,math,pathlib,sys,wave
path=pathlib.Path(sys.argv[1]);output=pathlib.Path(sys.argv[2])
assert not output.exists()
with wave.open(str(path),'rb') as w:
    assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(2,2,48000)
    frames=w.getnframes();raw=w.readframes(frames);assert len(raw)==frames*4
s=array.array('h',raw)
if sys.byteorder!='little':s.byteswap()
windows=[];size=960
for start in range(0,frames-size+1,size):
    channels=[s[start*2+c:(start+size)*2:2] for c in [0,1]];checks=[]
    for channel,period,wrong in zip(channels,[120,80],[80,120]):
        rms=math.sqrt(sum(v*v for v in channel)/size)
        def error(p):return math.sqrt(sum((channel[i]-channel[i-p])**2 for i in range(p,size))/(size-p))/rms if rms else None
        e,bad=error(period),error(wrong)
        checks.append(dict(rms=round(rms,3),period_error=e,other_channel_period_error=bad,valid=rms>10 and e is not None and e<0.06 and bad>0.1))
    windows.append(dict(start=start/48000,valid=all(v['valid'] for v in checks),channels=checks))
segments=[];first=None
for row in windows+[dict(start=frames/48000,valid=False)]:
    if row['valid'] and first is None:first=row['start']
    if not row['valid'] and first is not None:
        segments.append(dict(start=first,duration=round(row['start']-first,3)));first=None
long=[v for v in segments if v['duration']>=1.5]
short=[v for v in segments if 0.02<=v['duration']<0.3]
r=dict(scope=__doc__,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),frames=frames,seconds=frames/48000,segments=segments,complete_stereo_segments=len(long),reset_stereo_segments=len(short),passed=len(long)==8 and len(short)==4,physical_audibility=False)
output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
