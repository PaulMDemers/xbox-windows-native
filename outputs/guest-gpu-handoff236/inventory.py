"""Read owned dashboard/loader bytes and compiled watchpoint source without mutation."""
import struct,subprocess
from common import *
k=Path(__file__).resolve().parent;dest=k/'inventory001.json';assert not dest.exists()
art=k/'artifacts/inputs';art.mkdir(parents=True,exist_ok=False)
source=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet');pins=read(k.parent/'xemu-wait-snapshot234/candidate001-source-pins.json')
files={}
for n in ['gdbstub/system.c','gdbstub/gdbstub.c','accel/tcg/tcg-accel-ops.c','accel/tcg/watchpoint.c','system/watchpoint.c','target/i386/cpu.c','include/hw/core/cpu.h']:
 p=source/n;assert sha(p)==pins[n],n;q=art/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());files[n]=sha(q)
f=read(k.parent/'video-upload-runtime211/fixture-candidate001.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
m.fatx.PARTITIONS['C']=(0x465400*512,0xfa000*512)
with ColdIO(base) as io:
 rr=readers(io,base);rr['C']=m.Writer(io,m.fatx.open_partition(io,base,'C'))
 for v,path,name in [('C','evoxdash.xbe','dashboard.xbe'),('E','Applications/XWNFBoot/default.xbe','xromwell.xbe'),('E','Applications/XWNFBoot/freeldr.sys','freeldr.sys')]:
  data=rr[v].read(path);assert len(data)<=4*1024**2
  if v=='E':assert m.sha(data)==f['files'][v+'/'+path]
  else:assert m.sha(data)==read(k.parent/'native-windows-stage2/unleashx-fixture.json')['unleashx_xbe_sha256']
  (art/name).write_bytes(data);files[v+'/'+path]=m.sha(data)
assert sha(base)==f['fixture_sha256']
sys.path.insert(0,str(k));from parsing import xbe
dashboard=xbe((art/'dashboard.xbe').read_bytes());launcher=xbe((art/'xromwell.xbe').read_bytes())
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from validate_loader import validate
loader=validate((art/'freeldr.sys').read_bytes())
watch=(art/'source/accel/tcg/watchpoint.c').read_text();ops=(art/'source/accel/tcg/tcg-accel-ops.c').read_text();cpu=(art/'source/target/i386/cpu.c').read_text()
assert 'gdb_stop_before_watchpoint' not in cpu
assert 'cpu->cflags_next_tb = 1 | CF_NOIRQ' in watch and 'trigger after the current instruction' in watch
assert 'GDB_WATCHPOINT_WRITE' in ops and 'BP_STOP_BEFORE_ACCESS' in ops
save(dest,dict(passed=True,source_sha256=sha(Path(__file__)),files=files,parent_fixture_sha256=f['fixture_sha256'],dashboard=dashboard,launcher=launcher,freeldr=loader,gdb_watchpoint_stop='after completing the watched instruction; EIP is next instruction',physical_access=False,guest_launch=False,new_emulator_build=False,limits='Exact owned binary/compiled debugger source inputs; static launcher/FreeLoader entries are leads until resident executing bytes match. No old FreeLoader source rebuild claim.'))
print('236 owned binary/debugger inventory pinned')
