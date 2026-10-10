"""Author a NEW sacrificial reset guard kit; old evidence is read-only."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
assert not (k/'authored.json').exists()
parents={}
def donor(name):
 p=ws/name;parents[name]=hashlib.sha256(p.read_bytes()).hexdigest();return p.read_text(encoding='utf-8')
def write(name,text):
 p=k/name;assert not p.exists();p.write_text(text,encoding='utf-8',newline='\n')
for n in ['probe.c','trigger.c']:
 text=donor('outputs/video-shared-crash/'+n).replace('xwndump103','xwnguard221').replace('XwnDumpTest103','XwnGuardTest221').replace('0x103','0x221').replace('e058d103','e058d221').replace('E058D103','E058D221').replace('00000103','00000221').replace('30000','90000')
 write(n,text)
text=donor('outputs/video-shared-crash/Build.ps1')
text=text.replace("$ws=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)","$ws=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)\nif(Test-Path (Join-Path $PSScriptRoot artifacts)){throw 'Never rebuild same attempt'}")
write('Build.ps1',text)
text=donor('outputs/video-boot-layout219/Invoke-219.ps1').replace('blayout219-runs','reset221-runs')
write('Invoke-221.ps1',text)
text=donor('outputs/video-boot-layout219/Run.ps1').replace('blayout219','reset221').replace('Invoke-219','Invoke-221').replace('emulator-frozen.json','frozen.json').replace("$out=Join-Path $PSScriptRoot ('emu-'+$Case)","$out=Join-Path $PSScriptRoot $Case").replace('debugger=$false','debugger=$true').replace('-Seconds 480','-Seconds 540')
write('Run.ps1',text)
text=donor('outputs/video-boot-layout219/common.py');write('common.py',text)
text=donor('outputs/video-boot-layout219/Prepare.ps1').replace('prepare-emulator.py','prepare.py');write('Prepare.ps1',text)
(k/'authored.json').write_text(json.dumps({'dependencies':parents,'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in k.iterdir() if p.is_file()},'physical_access':False},indent=2)+'\n')
