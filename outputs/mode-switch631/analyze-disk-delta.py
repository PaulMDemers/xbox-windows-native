"""New analysis of closed631 disks; never changes or reruns their original audits."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ('emu001',)
out=k/case;dest=out/'disk-delta.json';assert not dest.exists()
assert json.loads((out/'host-closure.json').read_text(encoding='utf-8-sig'))['closed']
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
root=Path('/mnt/c/xwn631')/case
mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(root/'hdd.qcow2')],timeout=30))
rows=[];total=0;last=0;overlay=0;sha=lambda b:hashlib.sha256(b).hexdigest()
with ColdIO(root/'base.qcow2') as before,ColdIO(root/'hdd.qcow2') as after:
    assert before.size==after.size==8589934592
    for entry in mapping:
        assert entry['start']==last;last+=entry['length']
        if entry['depth']!=0:continue
        assert entry['length']<=32*1024**2;overlay+=entry['length']
        before.seek(entry['start']);a=before.read(entry['length'])
        after.seek(entry['start']);b=after.read(entry['length'])
        changes=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y];total+=len(changes)
        sectors=sorted(set(i//512 for i in changes));summaries=[]
        for sector in sectors:
            x=a[sector*512:(sector+1)*512];y=b[sector*512:(sector+1)*512]
            summaries.append(dict(offset=entry['start']+sector*512,bytes=512,before_sha256=sha(x),after_sha256=sha(y),changed_bytes=sum(v!=w for v,w in zip(x,y))))
        rows.append(dict(start=entry['start'],length=entry['length'],changed_bytes=len(changes),sectors=summaries))
    assert last==before.size
    before.seek(0x80000);after.seek(0x80000)
    first_partition_before=before.read(4096);first_partition_after=after.read(4096)
    assert first_partition_before[:4]==first_partition_after[:4]==b'FATX'
r=dict(case=case,read_only=True,complete_virtual_map_bytes=last,overlay_bytes_compared=overlay,changed_bytes=total,extents=rows,
    all_changed_sectors_below_first_partition=all(s['offset']+s['bytes']<=0x80000 for e in rows for s in e['sectors']),
    first_partition_header_equal=first_partition_before==first_partition_after,
    all_file_system_bytes_inherited_unchanged=all(e['start']+e['length']<=0x80000 for e in rows),
    original_whole_disk_equality_gate_still_failed=True,
    scope='Complete overlay comparison plus immutable backing identity from original audit. Changed reserved-area sectors are recorded, not waived or attributed to a specific writer.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
