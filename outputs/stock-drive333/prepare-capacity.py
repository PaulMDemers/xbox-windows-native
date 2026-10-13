"""Fresh capacity-only emulator fixture; no native Windows launch."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'video-text-oracle206'))
from common import ColdIO,readers,m,sha
assert os.environ.get('XWN_BUILD_LEASE')=='held'
out=K/'capacity-emu001';private=Path('/mnt/e/xwn333/capacity-emu001')
assert not out.exists() and not private.exists()
assert shutil.disk_usage('/mnt/c').free-64*1024**2>20*1024**3
assert shutil.disk_usage('/mnt/e').free-4*1024**3>20*1024**3
f=json.loads((K.parent/'artifact-recovery329/seed001/fixture.json').read_text())
base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
build=json.loads((K/'capacity-build001.json').read_text());assert build['compiled'] and build['sdk_unchanged']
xbe=Path('/mnt/e/xwn333/capacity-build001/bin/default.xbe').read_bytes()
assert m.sha(xbe)==build['outputs']['default.xbe']['sha256']
out.mkdir();private.mkdir(parents=True);target=private/'preparation.qcow2';source=private/'source.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
entry=rr['E'].write('Applications/XWNCapacity333/default.xbe',xbe);rr['E'].flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare',str(target),str(source)],check=True)
subprocess.run(['qemu-img','check',str(source)],check=True)
with ColdIO(source) as io:
    rr=readers(io,source);assert rr['E'].read('Applications/XWNCapacity333/default.xbe')==xbe
    geometry={v:dict(start=r.p.partition_offset,length=r.p.partition_size,unit=r.p.cluster_size,
                    total=(r.limit-1)*r.p.cluster_size,free=sum(x==0 for x in r.fat[1:r.limit])*r.p.cluster_size) for v,r in rr.items()}
assert sha(base)==f['fixture_sha256']
r=dict(parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_windows='E:'+str(source)[6:],
       fixture_path_linux=str(source),fixture_sha256=sha(source),file=entry,before_geometry=geometry,
       guest_launch=False,physical_access=False)
(out/'fixture.json').write_text(json.dumps(r,indent=2)+'\n');print('Capacity-only fixture prepared')
