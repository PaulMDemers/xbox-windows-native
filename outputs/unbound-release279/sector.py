"""Interpret one known reserved-sector delta; no new audit or image mutation."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'fatx-mapped-eof'))
from coldio import ColdIO
dest=k/'sector-analysis.json';assert not dest.exists()
root=Path('/mnt/e/xwn278/emu001');captures=[]
for name in ['base.qcow2','hdd.qcow2']:
    with ColdIO(root/name) as io:
        io.seek(1536);data=io.read(512)
    captures.append(data)
a,b=captures;assert a[:4]==b[:4]==b'BRFR'
changes=[dict(absolute=1536+i,before=x,after=y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
header=Path('/mnt/c/nxdk/lib/xboxkrnl/xboxkrnl.h');h=header.read_text()
begin=h.index('typedef struct _XBOX_REFURB_INFO');end=h.index('} XBOX_REFURB_INFO;',begin)+len('} XBOX_REFURB_INFO;')
declaration=h[begin:end];assert 'ULONG PowerCycleCount;' in declaration
r=dict(read_only=True,changes=changes,sector_before_sha256=hashlib.sha256(a).hexdigest(),
 sector_after_sha256=hashlib.sha256(b).hexdigest(),header_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),
 declaration=declaration,field_offset=4,power_cycle_count_before=int.from_bytes(a[4:8],'little'),
 power_cycle_count_after=int.from_bytes(b[4:8],'little'),
 interpretation='Delta matches the PowerCycleCount field of pinned nxdk XBOX_REFURB_INFO; boot-counter update is an inference, not captured writer attribution',
 actual_writer_proved=False,original_strict_equality_passed=False,original_audit_changed=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
