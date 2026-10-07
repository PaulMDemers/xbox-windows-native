"""Cold-read the actual loader override, not the unused Microsoft system copy."""
from common import *
phase=sys.argv[1];assert phase in ['before','after']
out=k/'trace001';dest=out/(phase+'-bootvid.json');assert not dest.exists()
f=read(k/'fixture-trace001.json');disk=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'] if phase=='before' else ws/'work/runs/nt5-vcache-trace001/hdd.qcow2'
if phase=='after':assert (disk.parent/'cleanup.json').exists()
with ColdIO(disk) as io:data=readers(io,disk)['E'].read('Applications/XWNFBoot/loader/xboxbvid.dll')
h=m.sha(data);assert h=='2196f646653c4c944d73fee4944ee3d056c82cf01903e4f435e67d63c03ed4b7'
p=out/'artifacts'/(phase+'-xboxbvid.dll');p.parent.mkdir(exist_ok=True);assert not p.exists();p.write_bytes(data)
save(dest,dict(path='E/Applications/XWNFBoot/loader/xboxbvid.dll',sha256=h,bytes=len(data),physical_access=False))
print('Loader bootvid override verified',phase,h)
