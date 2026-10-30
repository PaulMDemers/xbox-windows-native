"""Verify immutable owned Windows payload and create835 installation manifest. No FTP."""
import hashlib,json,sys
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=W/'outputs/boot720-native835';P=Path('C:/xwn835/package001');assert not P.exists();P.mkdir(parents=True)
sys.path.insert(0,str(W/'tools'));from stock_e import Package
pkg=Package('E:/xwn343/bundle002/stock-e-1080i-001.zip',W/'tools/stock-e-profile.json')
assert pkg.archive_sha256=='e79771fbf5eaf10c3e30e80e0d04e622dfd443448e24fa4eb76deac01d1b3e83'
cap=json.loads((W/'outputs/boot720-capacity834/collection001.json').read_text());assert cap['completed']
assert cap['e']['free_bytes']>pkg.allocated+256*1024**2
r={'verified':True,'physical_access':False,'archive_sha256':pkg.archive_sha256,'manifest_sha256':pkg.policy['manifest_sha256'],'files':{},'allocated_bytes':pkg.allocated,'capacity_record_sha256':hashlib.sha256((W/'outputs/boot720-capacity834/collection001.json').read_bytes()).hexdigest(),'startup_normal':True,'limits':'Private owned Windows clone for newly authorized1.6 installation. Existing343 installer same-console baseline gate is not reused; independent834 capacity and absent-root checks replace deployment identity. No console C or existing files are changed.'}
for path,meta in pkg.files.items():
 target=path.replace('/E/Applications/XWNEBoot/','/E/Applications/XWN16Boot835/')
 # New boot binaries are published last only after separate qualification.
 if path in ['/E/Applications/XWNEBoot/default.xbe','/E/Applications/XWNEBoot/freeldr.sys','/E/Applications/XWNEBoot/rosload.exe']:continue
 r['files'][target]={**meta,'archive_path':path}
startup=next(p for p in pkg.files if p.lower().endswith('/startup/xwnsetup.cmd'))
raw=pkg.read(startup);(P/'normal-startup.cmd').write_bytes(raw)
r['startup_sha256']=hashlib.sha256(raw).hexdigest()
r['directories']=sorted({p.replace('/E/Applications/XWNEBoot','/E/Applications/XWN16Boot835') for p in pkg.dirs},key=lambda p:(p.count('/'),p))
(K/'package001.json').write_text(json.dumps(r,indent=2)+'\n')
print('Verified',len(r['files']),'private payload files; allocation',r['allocated_bytes']);print('Normal startup:',raw.decode('ascii',errors='replace'))
