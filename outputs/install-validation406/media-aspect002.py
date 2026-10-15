"""Correct aspect ratio before any guest test; retain first derivative and receipt."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('E:/xwn406/media001');T=Path('E:/xwn406/transcoder001')
r=json.loads((K/'media-transcode001.json').read_text());exe=T/'ffmpeg.exe'
assert hashlib.sha256(exe.read_bytes()).hexdigest()==r['exe_sha256']
cmd=r['command'][:];cmd[cmd.index('-vf')+1]='scale=320:180:flags=lanczos,pad=320:240:0:30:black,setsar=1'
dest=P/'ces2001-nt5.mpg';assert not dest.exists();cmd[-1]=str(dest)
with (T/'convert002.log').open('xb') as f:assert subprocess.run(cmd,stdout=f,stderr=f,timeout=300).returncode==0
with (T/'decode002.log').open('xb') as f:assert subprocess.run([str(exe),'-v','error','-i',str(dest),'-f','null','-'],stdout=f,stderr=f,timeout=300).returncode==0
assert (T/'decode002.log').stat().st_size==0
r.update(command=cmd,output=str(dest),output_bytes=dest.stat().st_size,output_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),aspect='16:9 source preserved as 320x180 inside 320x240; black bars top/bottom',prior001='Unlaunched derivative distorted source aspect; preserved as failed presentation preparation')
with (K/'media-transcode002.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(r['output_sha256'])
