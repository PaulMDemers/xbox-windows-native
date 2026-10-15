"""Preserve collision failure; use a verified unused native output directory."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent
files=json.loads(Path('C:/xwn405/final-files001.json').read_text());assert not any(p.startswith('xwn409/') for p in files)
with (K/'stage002-failure.json').open('x') as f:json.dump(dict(reason='XWN406/probe.exe already belonged to the prior 405 diagnostic; writer refused overwrite',guest_launched=False,write_reached=False,source_unchanged_pending_complete_compare=True),f,indent=2)
for dest,src,changes in [('probe002.c','probe001.c',[('XWN406','XWN409')]),('build-probe002.py','build-probe001.py',[('probe-build001','probe-build002'),('probe001.c','probe002.c')])]:
    text=(K/src).read_text()
    for a,b in changes:text=text.replace(a,b)
    with (K/dest).open('x',newline='\n') as f:f.write(text)
s=(K/'stage002.py').read_text().replace('assembly002','assembly003').replace('probe-build001.json','probe-build002.json').replace('XWN406/','XWN409/')
a=s.index('measure=json.loads(');b=s.index('tree=ast.parse',a)
s=s[:a]+"assert shutil.disk_usage(P.parent).free-320*1024**2>=20*1024**3\n"+s[b:]
a=s.index("subprocess.run(['qemu-img','convert'");b=s.index("m.fatx.PARTITIONS",a)
s=s[:a]+"seed=P.parent/'assembly002/fresh.qcow2'\nassert subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(source),str(seed)],stdout=subprocess.DEVNULL).returncode==0\nwith (K/'stage002-readback.json').open('x') as f:json.dump(dict(seed_sha256=sha(seed),entire_virtual_disk_equals_source=True,never_launched=True),f,indent=2)\nsubprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../assembly002/fresh.qcow2',str(disk)],check=True)\n"+s[b:]
s=s.replace('standalone_flattened_copy=True','never_executed_flattened_seed=True')
with (K/'stage003.py').open('x',newline='\n') as f:f.write(s)
for name in ['Run001.ps1','Invoke001.ps1']:
    p=K/name;p.write_text(p.read_text().replace('assembly002','assembly003'),newline='\n')
