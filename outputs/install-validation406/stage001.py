"""Independent flattened continuation of audited 405; only three new files."""
import ast,json,shutil,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/e/xwn406/assembly001')
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
sys.path.insert(0,str(W/'outputs/fresh-assembly405'));from writeio001 import WriteIO
sys.path.insert(0,str(W/'tools'));from build_space import require_space
assert not P.exists();require_space(P,20+16/1024)
source=Path('/mnt/c/xwn405/runs/nt5-fresh405-emu006/hdd.qcow2')
assert sha(source)=='757fbba9179fb990451d7a586e7f6a1695d38cb988e106d3e1a81eaf4de73922'
measure=json.loads(subprocess.check_output(['qemu-img','measure','--output=json','-O','qcow2',str(source)]))
assert shutil.disk_usage(P.parent).free-measure['required']-320*1024**2>=20*1024**3
tree=ast.parse((W/'outputs/fresh-assembly405/normal-stage006.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'original405-inventory','exec'))
P.mkdir();disk=P/'fresh.qcow2'
subprocess.run(['qemu-img','convert','-f','qcow2','-O','qcow2',str(source),str(disk)],check=True)
assert subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(source),str(disk)],stdout=subprocess.DEVNULL).returncode==0
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(disk)])).get('backing-filename')
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(source) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,source,'E'));before=inventory(wr);assert STARTUP.lower() not in before
build=json.loads((K/'probe-build001.json').read_text())[0];assert build['exit_code']==0
media=json.loads((K/'media-transcode002.json').read_text());video=Path('/mnt/e/xwn406/media001/ces2001-nt5.mpg');assert sha(video)==media['output_sha256']
link=Path('/mnt/c/xwn405/extract004/files/Documents and Settings/Default User/SendTo/3\u00bd Floppy (A).lnk');assert sha(link)=='a17666e9f5ca27b79b5d8b925dcce3a6e60367031402a31278d354cace814b42'
exe=Path(build['path']);assert sha(exe)==build['sha256']
with WriteIO(disk,10000000000,P) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    changes=[wr.write('XWN406/probe.exe',exe.read_bytes()),wr.write('XWN406/floppy.lnk',link.read_bytes()),wr.write('XWN406/ces2001.mpg',video.read_bytes())]
    wr.flush();io.flush()
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'));after=inventory(wr)
expected=before.copy()
for row in changes:expected[row['path'].lower()]=row['sha256']
assert after==expected
r=dict(status='assembled-readback-verified',fixture_path_linux=str(disk),fixture_path_windows='E:/xwn406/assembly001/fresh.qcow2',fixture_sha256=sha(disk),source_sha256=sha(source),source_unchanged=True,standalone_flattened_copy=True,scope='Audited installation continuation, not a new clean-install qualification',physical_access=False,changes=changes,normal_startup_unchanged=True,all_other_file_bytes_exact=True,before_files=len(before),after_files=len(after),disk_check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)])))
with (K/'assembly001.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({k:r[k] for k in ['status','before_files','after_files','fixture_sha256']}))
