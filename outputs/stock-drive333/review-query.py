"""Separate kernel-visible geometry from historical expanded-fixture geometry."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'capacity-emu003/query-review.json';assert not dest.exists()
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha
f=json.loads((K/'capacity-emu003/fixture.json').read_text());p=Path(f['fixture_path_linux']);assert sha(p)==f['fixture_sha256']
a=json.loads((K/'capacity-emu003/cold-audit003.json').read_text());rows=a['queries']
# Standard partition1 ends at the independently recorded partition6 start.
start=5633024*512;end=15633072*512;length=end-start
old=m.fatx.PARTITIONS['E'];m.fatx.PARTITIONS['E']=(start,length)
with ColdIO(p) as io:
    w=m.Writer(io,m.fatx.open_partition(io,p,'E'))
    expected=dict(start=start,length=length,unit=w.p.cluster_size,total=(w.limit-1)*w.p.cluster_size,free=sum(x==0 for x in w.fat[1:w.limit])*w.p.cluster_size)
    exact=all(rows[0][n]==v for n,v in expected.items())
    assert exact
m.fatx.PARTITIONS['E']=old
r=dict(e_query_verified=exact,expected_e=expected,historical_e_length=old[1],
       historical_e_geometry_issue='Shared staging tool E length exceeds standard E end by 12754944 bytes; rounded FAT size coincides, so directory/data offsets agree but free-count bound does not. Do not use that oversized bound for new stock fixtures.',
       f_query=dict(reported=rows[1],expanded_fixture_length=472764096*512,
         observed_end=rows[1]['start']+rows[1]['length'],lba28_last_sector_end=(2**28-1)*512,
         interpretation='Reported F ends at LBA28 last-sector boundary while the fixture uses an expanded table and FAT. Likely legacy BIOS geometry; not physical-console free space and not a qualified F query oracle.'),
       overall_original_audit_passed=a['passed'],host_orderly=a['host_exit']['passed'],
       scope='E query and exclusive report lifecycle verified. Original full geometry comparison remains failed; no disk change or historical requalification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
