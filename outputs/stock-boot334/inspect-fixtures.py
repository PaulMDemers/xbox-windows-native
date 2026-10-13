import sys,json,struct
from pathlib import Path
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/stock-boot334')
sys.path.insert(0,str(k.parent/'video-text-oracle206'))
from common import ColdIO,readers,m,STARTUP
p=Path('/mnt/e/xwn329/seed001/source.qcow2')
with ColdIO(p) as io:
 r=readers(io,p)
 print('Froot',[(n,int.from_bytes(e[2][48:52],'little'),bool(e[2][1]&16)) for n,e in r['F'].directory(1)['entries'].items()])
 print('Eroot',list(r['E'].directory(1)['entries']))
 print('startup',repr(r['F'].read(STARTUP)))
 d=r['E'].directory(1)['entries']['applications'][2];d=r['E'].directory(int.from_bytes(d[44:48],'little'))['entries']['xwnfboot'][2]
 print('launcher',list(r['E'].directory(int.from_bytes(d[44:48],'little'))['entries']))
 p=Path('/mnt/c/Emulators/xemu/system/xbox_hdd.qcow2')
with ColdIO(p) as io:
 io.seek(0);print('blanktable',repr(io.read(512)[:32]))
 for label,off in [('E',5633024*512),('C',4609024*512)]:
  io.seek(off);print('blank',label,io.read(512)[:16].hex())
