"""Independent source/video and speech-envelope comparison of the actual WMP run."""
import hashlib,json,subprocess,wave
from pathlib import Path
import numpy as np
from PIL import Image
K=Path(__file__).resolve().parent;P=Path('E:/xwn406/media-evidence001');P.mkdir(exist_ok=False)
exe=Path('E:/xwn406/transcoder001/ffmpeg.exe');source=Path('E:/xwn406/media001/ces2001-nt5.mpg');capture=Path('E:/xwn406/runs/nt5-validation406-emu001/ac97-output.wav')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(exe)=='2ce797a0f88d7f067180338fb227f7b1928ea727bd9a4d7a1d022f7c52af71a3'
assert sha(source)=='e39bf2aee01eecf993723988b274518f3f75076c6b62d1f263051daadd069619'
def ff(args):
    r=subprocess.run([str(exe),'-nostdin','-v','error','-n',*args],capture_output=True,timeout=120)
    assert r.returncode==0,r.stderr.decode(errors='replace')
    return r
audio={}
for name,path in [('source',source),('captured',capture)]:
    pcm=P/(name+'.pcm');ff(['-i',str(path),'-vn','-ac','1','-ar','8000','-f','s16le',str(pcm)])
    a=np.fromfile(pcm,dtype='<i2').astype(np.float64)
    # Twenty millisecond, phase-independent envelope tolerates codec/resampler differences.
    blocks=a[:len(a)//160*160].reshape(-1,160)
    energy=np.log1p(np.sqrt(np.mean(blocks*blocks,axis=1)))
    audio[name]=dict(samples=len(a),duration_seconds=len(a)/8000,rms=float(np.sqrt(np.mean(a*a))),peak=float(np.max(np.abs(a))),sha256=sha(path))
    if name=='source':y=energy
    else:x=energy
def match(a,b):
    assert len(a)>=len(b)>100
    b=b-b.mean();n=len(b)
    sums=np.concatenate(([0.],np.cumsum(a)));squares=np.concatenate(([0.],np.cumsum(a*a)))
    variance=np.maximum(squares[n:]-squares[:-n]-(sums[n:]-sums[:-n])**2/n,1e-12)
    corr=np.correlate(a,b,mode='valid')/np.sqrt(variance*np.sum(b*b))
    i=int(np.argmax(corr));return dict(score=float(corr[i]),offset_seconds=i*.02)
full=match(x,y)
negatives=dict(reversed=match(x,y[::-1]),shuffled=match(x,np.random.default_rng(406).permutation(y)))
assert full['score']>.8 and all(v['score']<full['score']-.25 for v in negatives.values()),(full,negatives)
assert audio['captured']['rms']>100
raw=P/'source-frames.rgb';ff(['-i',str(source),'-an','-vf','fps=1,scale=80:60','-pix_fmt','rgb24','-f','rawvideo',str(raw)])
frames=np.fromfile(raw,dtype=np.uint8).reshape(-1,60,80,3).astype(np.float32)
video=[]
for name in ['frame009.png','frame010.png']:
    path=Path('E:/xwn406')/name;im=Image.open(path).convert('RGB');best=None
    # The independently observed WMP client rectangle is approximately (527,325), 320x240.
    # Search only its border uncertainty; never change source frames or expected content.
    for top in range(323,330):
        for left in range(526,532):
            crop=np.asarray(im.crop((left,top,left+320,top+240)).resize((80,60),Image.Resampling.BILINEAR),dtype=np.float32)
            error=np.mean(np.abs(frames-crop),axis=(1,2,3));index=int(np.argmin(error))
            row=dict(frame=name,source_second=index,mean_absolute_rgb_error=float(error[index]),crop=[left,top,320,240],sha256=sha(path))
            if best is None or row['mean_absolute_rgb_error']<best['mean_absolute_rgb_error']:best=row
    video.append(best)
assert all(v['mean_absolute_rgb_error']<15 for v in video) and abs(video[0]['source_second']-video[1]['source_second'])>10,video
r=dict(audio=audio,full_clip_envelope_match=full,audio_negative_controls=negatives,video_matches=video,
       emulator_wmp_audio_video_scoped_pass=True,physical_tv_or_speaker_confirmation=False,
       scope='Actual Windows Media Player screenshots and captured emulated AC97 output match the requested MPEG derivative; not physical sound routing, subjective quality or zero dropped-frame certification.',
       private_files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in P.iterdir() if p.is_file()})
with (K/'media-evidence001.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({k:r[k] for k in ['full_clip_envelope_match','audio_negative_controls','video_matches','emulator_wmp_audio_video_scoped_pass']}))
