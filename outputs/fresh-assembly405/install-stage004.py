"""Continue the same clean installation in a NEW child after audited normal restart."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/assembly004');assert not P.exists()
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
from writeio001 import WriteIO
audit=json.loads((K/'emu004/audit.json').read_text());assert audit['core_boot_scoped_passed'] and audit['checks']['normal_restart']
parent=Path('/mnt/c/xwn405/runs/nt5-fresh405-emu004/hdd.qcow2');assert sha(parent)==audit['disk_sha256']
r=json.loads((K/'assembly003.json').read_text());build=json.loads((K/'probe-build004.json').read_text());assert all(v['exit_code']==0 for v in build)
P.mkdir();disk=P/'fresh.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../runs/nt5-fresh405-emu004/hdd.qcow2',str(disk)],check=True)
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
changes=[]
startup=b'@echo off\r\nC:\\XWN407\\probe.exe\r\n'
with WriteIO(disk,10000000000,P) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    for name,record in [('XWN407/probe.exe',build[0])]:
        p=Path(record['path']);assert sha(p)==record['sha256'];row=wr.write(name,p.read_bytes());changes.append(row)
        r['files'].append(row);r['sources'][name.lower()]=dict(kind='fresh405 installation witness',sha256=row['sha256'])
    m.replace(wr,STARTUP,startup);wr.flush();io.flush()
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    for row in changes:assert m.sha(wr.read(row['path']))==row['sha256']
    assert wr.read(STARTUP)==startup
r.update(fixture_path_linux=str(disk),fixture_path_windows='C:'+str(disk)[6:],fixture_sha256=sha(disk),parent_sha256=sha(parent),
         parent_never_executed=False,parent_role='Same fresh installation after audited ordinary boot/normal restart; not a fresh independent control',
         previous_case='emu004',boot_qualified=False,changes=changes,normal_startup_replaced=True,startup_sha256=m.sha(startup))
for row in r['files']:
    if row['path'].lower()==STARTUP.lower():row.update(bytes=len(startup),sha256=m.sha(startup))
r['sources'][STARTUP.lower()]=dict(kind='Post-install reboot with bounded audio and network witness; no reinstall',sha256=m.sha(startup))
r['qcow_check']=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)]))
(K/'assembly004.json').write_text(json.dumps(r,indent=2)+'\n');print('Next clean-installation phase prepared; no driver service or PnP registry fabrication')
