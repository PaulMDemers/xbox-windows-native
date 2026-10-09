"""Read-only journal preservation from CLOSED194, not recovery or another trial collection."""
import contextlib
import datetime
import struct
from common import *

prior = k.parent / 'video-measurement-boundary194'
out = k / 'journal194'
assert read(prior / 'pending001/closure.json')['closed'] and not out.exists()
out.mkdir()
art = out / 'artifacts'
art.mkdir()
f = read(prior / 'fixture-pending001.json')
base = ws / 'outputs/native-windows-fatx-forensics/artifacts' / f['fixture_name']
disk = ws / 'work/runs/nt5-boundary194-pending001/hdd.qcow2'
assert sha(base) == f['fixture_sha256']
disk_sha = sha(disk)
r = dict(read_only=True, recovery_attempted=False, physical_access=False,
         source_sha256=sha(Path(__file__)), closed_audit_sha256=sha(prior / 'pending001/audit.json'),
         utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), disk_sha256=disk_sha,
         files=[], limits='Raw header fields and journal bytes only; no log replay, repair, '
         'producer attribution or claim that raw hive damage survives journal recovery.')
with contextlib.ExitStack() as stack:
    rr = [readers(stack.enter_context(ColdIO(p)), p) for p in [base, disk]]
    for phase, reader in zip(['before', 'after'], rr):
        for name in ['system', 'system.log', 'system.alt', 'system.sav']:
            row = dict(phase=phase, name=name)
            try:
                data = reader['F'].read('winnt/system32/config/' + name)
            except KeyError:
                row['present'] = False
            else:
                dest = art / (phase + '-' + name)
                dest.write_bytes(data)
                row.update(present=True, bytes=len(data), sha256=sha(dest), first64=data[:64].hex())
                if len(data) >= 512 and data[:4] == b'regf':
                    row.update(regf_header=True, sequences=list(struct.unpack_from('<II', data, 4)),
                               raw_file_type=struct.unpack_from('<I', data, 28)[0],
                               raw_hbins_length=struct.unpack_from('<I', data, 40)[0])
                else:
                    row['regf_header'] = False
            r['files'].append(row)
assert sha(base) == f['fixture_sha256'] and sha(disk) == disk_sha
save(out / 'capture.json', r)
print(json.dumps(r, indent=2))
