"""Complete preboot cold audits and freeze a unique stock-E runtime."""
import ast,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';assert not out.exists()
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
from stock_io002 import readers,scan
seed=json.loads((K/'seed003/fixture.json').read_text());assert seed['prepared']
disk=Path(seed['fixture_path_linux']);assert sha(disk)==seed['fixture_sha256']
scan(disk,K/'seed003/review002/artifacts')
a=json.loads((K/'seed003/review002/allocation.json').read_text());assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
out.mkdir();art=out/'artifacts';art.mkdir()
parent=json.loads((K.parent/'artifact-recovery329/seed001/fixture.json').read_text())
files={'E/'+v['path']:v['sha256'] for v in seed['files']}
lookup={p.lower():h for p,h in files.items()};files['E/'+STARTUP]=lookup[('E/'+STARTUP).lower()]
protected={}
for path in parent['protected']:
    v,p=path.split('/',1)
    if v=='E':p=p.replace('XWNFBoot','XWNEBoot')
    new='E/'+p;protected[new]=lookup[new.lower()]
with ColdIO(disk) as io:
    rr=readers(io,disk)
    for n in ['system','software','default','sam','security']:(art/('before-'+n)).write_bytes(rr['E'].read('winnt/system32/config/'+n))
    assert rr['E'].read(STARTUP)==b'@echo off\r\nC:\\xwndemo251\\runner.exe /emulator\r\nexit\r\n'
    io.seek(0);assert io.read(512)==bytes(512)
f=dict(fixture_path_linux=str(disk),fixture_path_windows=seed['fixture_path_windows'],fixture_sha256=seed['fixture_sha256'],parent='/mnt/e/xwn329/seed001/source.qcow2',parent_sha256=seed['parent_sha256'],namespace='xwndemo251',files=files,protected=protected,stock_disk_bytes=seed['bytes'],extended_F_present=False,physical_access=False)
(out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
paths=list(K.glob('*.py'))+list(K.glob('*.ps1'))+[out/'fixture.json',K/'seed003/fixture.json',K.parent/'stock-boot334/binary-review003.json']
for folder in ['video-text-oracle206','native-windows-fatx-runtime','native-windows-nt5-kernel','native-windows-paint-save','fatx-mapped-eof']:
    paths+=list((K.parent/folder).glob('*.py'))
paths += [K.parent/n for n in ['surface-bridge260/atomic_json.py','gpu-reset-banner152/ftp_deadline.py','native-windows-prebuild/monitor_capture.py','native-windows-prebuild/launch_unleashx.py','native-windows-physical-f/decode-legacy-events.py']]
pins={str(p.relative_to(W)):sha(p) for p in paths}
for p in paths:
    if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
(K/'emulator-frozen.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Stock preboot allocation and frozen source checks passed',len(pins),flush=True)
