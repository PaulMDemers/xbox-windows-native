"""Pinned private transcoder; MPEG-1/MP2 derivative for NT5 WMP testing."""
import hashlib,json,shutil,subprocess,urllib.request,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('E:/xwn406/media001');T=Path('E:/xwn406/transcoder001');T.mkdir(exist_ok=False)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
url='https://files.pythonhosted.org/packages/2c/c6/fa760e12a2483469e2bf5058c5faff664acf66cadb4df2ad6205b016a73d/imageio_ffmpeg-0.6.0-py3-none-win_amd64.whl'
assert shutil.disk_usage(T).free-200*1024**2>=20*1024**3
wheel=T/'transcoder.whl'
with urllib.request.urlopen(url,timeout=30) as r,wheel.open('xb') as f:
    count=0
    while b:=r.read(1024**2):
        count+=len(b);assert count<=31246824;f.write(b)
assert count==31246824 and sha(wheel)=='02fa47c83703c37df6bfe4896aab339013f62bf02c5ebf2dce6da56af04ffc0a'
with zipfile.ZipFile(wheel) as z:
    name=next(n for n in z.namelist() if n.endswith('.exe'))
    exe=T/'ffmpeg.exe';exe.write_bytes(z.read(name))
source=P/'ces2001-source.mp4';assert sha(source)=='2c2a3a109dc44710244eaca4e5b32388b801f05d09e409be2dec80614e70fb9c'
dest=P/'ces2001.mpg';assert not dest.exists()
cmd=[str(exe),'-nostdin','-hide_banner','-n','-i',str(source),'-map','0:v:0','-map','0:a:0',
     '-vf','scale=320:240:flags=lanczos,setsar=1','-r','30000/1001','-c:v','mpeg1video',
     '-b:v','700k','-maxrate','900k','-bufsize','327680','-g','15','-pix_fmt','yuv420p',
     '-c:a','mp2','-ar','44100','-ac','2','-b:a','128k','-f','mpeg',str(dest)]
with (T/'convert.log').open('xb') as log:result=subprocess.run(cmd,stdout=log,stderr=log,timeout=300)
assert result.returncode==0
with (T/'decode.log').open('xb') as log:
    decode=subprocess.run([str(exe),'-nostdin','-v','error','-i',str(dest),'-f','null','-'],stdout=log,stderr=log,timeout=300)
assert decode.returncode==0 and (T/'decode.log').stat().st_size==0
record=dict(tool_url=url,wheel_sha256=sha(wheel),exe_sha256=sha(exe),source_sha256=sha(source),
            command=cmd,output=str(dest),output_bytes=dest.stat().st_size,output_sha256=sha(dest),
            full_host_decode=True,guest_wmp_playback=False,physical_audio_confirmation=False,
            scope='Scaled/transcoded private playback derivative; source retained, no footage included in public bundle')
with (K/'media-transcode001.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
