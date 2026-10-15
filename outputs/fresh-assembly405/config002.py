"""New never-booted assembly child fixing only the required FreeLoader INI section."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/assembly002');assert not P.exists()
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
from writeio001 import WriteIO
r=json.loads((K/'assembly001.json').read_text());parent=Path(r['fixture_path_linux']);assert sha(parent)==r['fixture_sha256']
assert json.loads((K/'emu001/audit.json').read_text())['host_exit']['passed']
config=b'[FreeLoader]\r\nTimeOut=0\r\n[XwnProbe]\r\nToken=XWN-SECOND-STAGE-20261003\r\n'
# The inspected pinned loader requires this section before UiInitialize.
settings=Path('/home/paul/xbox-windows-native/release-readiness403-loader001/source/boot/freeldr/freeldr/settings.c')
assert b'Bootloader section not found in freeldr.ini' in settings.read_bytes()
P.mkdir();disk=P/'fresh.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../assembly001/fresh.qcow2',str(disk)],check=True)
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with WriteIO(disk,10000000000,P) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'));m.replace(wr,'Applications/XWNEBoot/freeldr.ini',config);wr.flush();io.flush()
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    for row in r['files']:
        expected=m.sha(config) if row['path'].lower()=='applications/xwneboot/freeldr.ini' else row['sha256']
        assert m.sha(wr.read(row['path']))==expected,row['path']
        if row['path'].lower()=='applications/xwneboot/freeldr.ini':row.update(bytes=len(config),sha256=expected)
r.update(fixture_path_linux=str(disk),fixture_path_windows='C:'+str(disk)[6:],fixture_sha256=sha(disk),
         parent_sha256=sha(parent),parent_never_executed=True,config_source_sha256=sha(settings),config_text=config.decode(),boot_qualified=False)
r['sources']['applications/xwneboot/freeldr.ini']=dict(kind='generated required FreeLoader and preflight sections',sha256=m.sha(config))
r['qcow_check']=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)]))
(K/'assembly002.json').write_text(json.dumps(r,indent=2)+'\n');print('New configuration child and all file hashes verified')
