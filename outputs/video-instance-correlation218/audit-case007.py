"""Read one CLOSED218 child once, including failed/missing app evidence."""
import json,sys,hashlib,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-gpu-handoff216'))
from common import ColdIO,readers,hive,scan,sha,read,m,HIVES
run=Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/instance218-runs/stock-instance218-epath007')
assert (run/'cleanup.json').exists()
out=k/'emu-epath007';assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
seed=Path('/mnt/e/Codex-archive/xbox-windows-native/gstate216/control001-source.qcow2')
assert sha(seed)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256']
disk=run/'hdd.qcow2';assert read(run/'disk-retention.json')['retained']
f=read(ws/'outputs/video-gpu-handoff216/fixture-control001.json')
r=dict(debugger=False,physical_access=False,nt5_launched=False,files=[],hives=[],probe_files={},closed=True)
m.fatx.PARTITIONS['C']=(0x465400*512,0xfa000*512)
with ColdIO(disk) as io:
    rr=readers(io,disk);c=m.Writer(io,m.fatx.open_partition(io,disk,'C'))
    r['c_root_entries']=list(c.directory(1)['entries'])
    for name,digest in f['files'].items():
        v,path=name.split('/',1);actual=m.sha(rr[v].read(path))
        r['files'].append(dict(path=name,expected=digest,actual=actual,matched=digest==actual))
    for name in HIVES:
        p=art/name;p.write_bytes(rr['F'].read('winnt/system32/config/'+name));r['hives'].append(dict(name=name,**hive(p)))
    for name in ['report.txt','cpu0.bin','gpu0.bin','cpu1.bin','gpu1.bin']:
        try:blob=rr['E'].read('xwninst218d/'+name)
        except KeyError:r['probe_files'][name]=dict(present=False);continue
        p=art/name;p.write_bytes(blob);r['probe_files'][name]=dict(present=True,bytes=len(blob),sha256=m.sha(blob))
    r['bytes_read']=io.read_bytes
scan(disk,art/'allocation');a=read(art/'allocation.json')
r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['matched'] for v in r['files']) and all(v['parsed'] for v in r['hives'])
r['probe_completed']=all(v['present'] for v in r['probe_files'].values())
if r['probe_completed']:
    text=(art/'report.txt').read_text();r['report']=text
    r['probe_completed'] &= 'COMPLETE 1 LOG_OK 1 STOCK_RESTART_REQUEST' in text
    r['raw_lengths_passed']=all(r['probe_files'][n]['bytes']==0x5000 for n in ['cpu0.bin','gpu0.bin','cpu1.bin','gpu1.bin'])
    if r['raw_lengths_passed']:
        c0,c1,g0,g1=[struct.unpack('<5120I',(art/n).read_bytes()) for n in ['cpu0.bin','cpu1.bin','gpu0.bin','gpu1.bin']]
        inv=tuple(v for b in reversed([c0[i:i+4] for i in range(0,len(c0),4)]) for v in b)
        r['independent_comparison']=dict(cpu_stable=c0==c1,gpu_stable=g0==g1,nonzero_words=sum(v!=0 for v in c0),distinct_blocks=len(set(c0[i:i+4] for i in range(0,len(c0),4))),forward_mismatches=sum(x!=y for x,y in zip(c0,g0)),reverse16_mismatches=sum(x!=y for x,y in zip(inv,g0)))
r.update(parent_unchanged=sha(seed)==read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256'],disk_sha256=sha(disk),cleanup_sha256=sha(run/'cleanup.json'),gpu_alias_proven=False,nt5_ownership_granted=False,physical_qualified=False)
(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['integrity_passed','probe_completed','c_root_entries','probe_files']},indent=2))
