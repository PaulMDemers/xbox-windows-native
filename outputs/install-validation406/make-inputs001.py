"""Prepare new case-specific scripts; never modify any frozen 405 input."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'fresh-assembly405'
def save(name,s):
    with (K/name).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
s=(K/'archive-executables001.py').read_text();a=s.index('names=[');b=s.index('\nout=',a)
names=[('renderer259-build001','xemu-renderer259.exe'),('bridge260-build001','xemu-bridge260.exe'),
       ('reuse269-build005','xemu-reuse269.exe'),('ledger265-build003','xemu-ledger265.exe'),
       ('boundary278-build002','xemu-boundary278.exe'),('runtime281-build001','xemu-runtime281.exe')]
s=s[:a]+'names='+repr(names)+s[b:];save('archive-executables002.py',s.replace('archive-executables001.json','archive-executables002.json'))
s=(old/'build-probe005.py').read_text().replace('/mnt/c/xwn405/probe-build005','/mnt/e/xwn406/probe-build001').replace('probe005.c','probe001.c').replace('probe-build005.json','probe-build001.json')
save('build-probe001.py',s)
s=(old/'Invoke005.ps1').read_text().replace('C:/xwn405/runs','E:/xwn406/runs').replace('/mnt/c/xwn405/runs','/mnt/e/xwn406/runs').replace('C:/xwn405/assembly006/fresh.qcow2','E:/xwn406/assembly001/fresh.qcow2').replace('../../assembly006/fresh.qcow2','../../assembly001/fresh.qcow2')
save('Invoke001.ps1',s)
for name in ['start-owned.ps1','close-host.py']:save(name,(old/name).read_text())
s=(old/'Run006.ps1').read_text().replace('emu006','emu001').replace('assembly006.json','assembly001.json').replace('Invoke005.ps1','Invoke001.ps1').replace('nt5-fresh405-emu001','nt5-validation406-emu001')
s=s.replace('(Get-PSDrive C).Free-256MB -lt 20GB -or (Get-PSDrive E).Free-32MB -lt 20GB','(Get-PSDrive C).Free-16MB -lt 20GB -or (Get-PSDrive E).Free-256MB -lt 20GB')
# Output disk/audio/scratch now all on E; reused immutable closed portable avoids another executable copy.
save('Run001.ps1',s)
s=(old/'supervise006.py').read_text().replace("['emu006']","['emu001']").replace('C:/xwn405/runs/nt5-fresh405-','E:/xwn406/runs/nt5-validation406-')
save('supervise001.py',s)
s=(old/'logon-owned002.py').read_text().replace('C:/xwn405/runs/nt5-fresh405-emu006','E:/xwn406/runs/nt5-validation406-emu001').replace("'emu006'","'emu001'")
save('logon-owned001.py',s)
