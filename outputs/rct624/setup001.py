"""Create a fresh control kit; all closed predecessor files are read-only inputs."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct623'
for name in ['vm.py','cold002.py','prepare001.py','actions002.py','input_transport001.py','serial_host.py']:
 p=K/name;assert not p.exists();s=(old/name).read_text().replace('623','624')
 if name=='vm.py':s=s.replace('capture=time.monotonic()+5','capture=time.monotonic()+60')
 p.write_text(s)
s=(old/'build001.py').read_text().replace('623','624').replace("[('subject.c','subject.exe'),('runner.c','run624.exe')]","[('subject.c','RCT.EXE'),('launcher.c','play624.exe')]")
s=s.replace("'-Wl,--subsystem,console:5.0'","'-Wl,--subsystem,windows:5.0'")
(K/'build001.py').write_text(s)
(K/'edition.json').write_text('{"fixture":"/mnt/c/xwn624/pc001"}\n')
