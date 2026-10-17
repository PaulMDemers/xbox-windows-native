"""New FATX continuation, adding only the two EXACT tested423 binaries."""
import ast,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn424/assembly001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
sys.path.insert(0,str(W/'outputs/install-validation406'));from oem_reader import OemReader
sys.path.insert(0,str(W/'tools'));from build_space import require_space
assert not P.exists() and not (K/'assembly001.json').exists()
space=require_space(P,20+32/1024)
source=Path('/mnt/e/xwn406/runs/nt5-validation406-emu001/hdd.qcow2')
prior=json.loads((W/'outputs/install-validation406/emu001/audit.json').read_text())
assert sha(source)==prior['disk_sha256'] and prior['host_exit']['passed']
proof=json.loads((W/'outputs/crypto-persistence423/ntfs-independent001.json').read_text());assert proof['passed'] and proof['closed'] and proof['disk_unchanged']
build=json.loads((W/'outputs/crypto-persistence423/build001.json').read_text())
tree=ast.parse((W/'outputs/fresh-assembly405/normal-stage006.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory');exec(compile(ast.Module(body=[fn],type_ignores=[]),'original405-inventory','exec'))
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(source) as io:
 wr=OemReader(io,m.fatx.open_partition(io,source,'E'));before=inventory(wr)
 assert STARTUP.lower() not in before and not any(p.startswith(('xwn423/','xwn423bin/')) for p in before)
P.mkdir(parents=True);disk=P/'fresh.qcow2'
backing=os.path.relpath(source,P);assert backing=='../../xwn406/runs/nt5-validation406-emu001/hdd.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',backing,str(disk)],check=True,stdout=subprocess.DEVNULL)
with WriteIO(disk,10000000000,P) as io:
 wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'));changes=[]
 for row in build['rows']:
  exe=Path(row['path']);assert sha(exe)==row['sha256'];changes.append(wr.write('XWN423BIN/'+row['name'],exe.read_bytes()))
 wr.flush();io.flush()
with ColdIO(disk) as io:after=inventory(OemReader(io,m.fatx.open_partition(io,disk,'E')))
expected=before.copy()
for row in changes:expected[row['path'].lower()]=row['sha256']
assert after==expected and sha(source)==prior['disk_sha256']
record={'status':'assembled-readback-verified','space':space,'source_sha256':sha(source),'source':str(source),'fixture_path_linux':str(disk),'fixture_path_windows':'E:/xwn424/assembly001/fresh.qcow2','fixture_sha256':sha(disk),'changes':changes,'before_files':len(before),'after_files':len(after),'all_other_file_bytes_exact':True,'startup_unchanged':True,'disk_check':json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)])),'physical_access':False,'scope':'New disposable continuation of closed406; paired APIs with423NTFS, not an identical hardware/configuration control or new clean ISO install'}
(K/'assembly001.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'before':len(before),'after':len(after),'other_files_exact':True}))
