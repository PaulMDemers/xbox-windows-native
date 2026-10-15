"""Remove only the owned diagnostic startup in a new audited installation child."""
import json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/assembly006');assert not P.exists()
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
from writeio001 import WriteIO
def inventory(w):
    result={};pending=[('',1)];seen=set()
    for prefix,c in pending:
        assert c not in seen;seen.add(c)
        for name,(_,_,e) in w.directory(c)['entries'].items():
            path=prefix+name
            if e[1]&16:
                first=struct.unpack_from('<I',e,44)[0]
                if first:pending.append((path+'/',first))
                else:assert struct.unpack_from('<I',e,48)[0]==0,'Nonempty zero-cluster directory'
            else:result[path]=m.sha(w.read(path))
    return result
audit=json.loads((K/'emu005/audit.json').read_text());assert audit['runtime_components_all_passed']
parent=Path('/mnt/c/xwn405/runs/nt5-fresh405-emu005/hdd.qcow2');assert sha(parent)==audit['disk_sha256']
r=json.loads((K/'assembly004.json').read_text());build=json.loads((K/'probe-build005.json').read_text())[0];assert build['exit_code']==0
P.mkdir();disk=P/'fresh.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b','../runs/nt5-fresh405-emu005/hdd.qcow2',str(disk)],check=True)
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(parent) as io:
    w=m.Writer(io,m.fatx.open_partition(io,parent,'E'));before=inventory(w);old=w.read(STARTUP)
assert m.sha(old)==r['startup_sha256']
with WriteIO(disk,10000000000,P) as io:
    w=m.Writer(io,m.fatx.open_partition(io,disk,'E'))
    exe=Path(build['path']);assert sha(exe)==build['sha256']
    changes=[w.write('XWN408/probe.exe',exe.read_bytes()),w.write('XWN408/previous-startup.cmd',old)]
    at=1;parts=w.parts(STARTUP)
    for name in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name.lower()][2],44)[0]
    dc,off,e=w.directory(at)['entries'][parts[-1].lower()];assert not e[1]&16
    clusters=list(w.chain(struct.unpack_from('<I',e,44)[0]))
    assert w.read(STARTUP)==old
    b=bytearray(w.read_cluster(dc));b[off]=229;w.write_cluster(dc,b)
    for c in clusters:w.fat[c]=0
    w.dirs.clear();w.flush();io.flush()
with ColdIO(disk) as io:
    w=m.Writer(io,m.fatx.open_partition(io,disk,'E'));after=inventory(w)
expected=before.copy();del expected[STARTUP.lower()]
for row in changes:expected[row['path'].lower()]=row['sha256']
assert after==expected,'Unexpected file namespace/content mutation'
r['files']=[v for v in r['files'] if v['path'].lower()!=STARTUP.lower()]+changes
del r['sources'][STARTUP.lower()]
for row in changes:r['sources'][row['path'].lower()]=dict(kind='fresh405 manual validation; not startup',sha256=row['sha256'])
r.update(fixture_path_linux=str(disk),fixture_path_windows='C:'+str(disk)[6:],fixture_sha256=sha(disk),parent_sha256=sha(parent),previous_case='emu005',boot_qualified=False,
         diagnostic_startup_absent=True,normal_startup_replaced=False,changes=changes,removed_startup_sha256=m.sha(old),startup_sha256=None,
         all_existing_files_exact_except_removed_startup=True,before_files=len(before),after_files=len(after),freed_startup_clusters=len(clusters))
r['qcow_check']=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(disk)]))
(K/'assembly006.json').write_text(json.dumps(r,indent=2)+'\n');print('Normal startup restored; all other existing file bytes exact')
