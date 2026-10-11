"""Correlate host block request-entry records with independently read cold FATX extents."""
import collections, hashlib, json, re, sys
from pathlib import Path

k = Path(__file__).resolve().parent
case = sys.argv[1]
assert case in ['emu001','emu002']
run = k.parents[1] / ('work/runs/nt5setup-' + case)
assert (run / 'cleanup.json').exists()
raw = (run / 'host-io.trace').read_bytes()
assert len(raw) <= 130 * 1024 * 1024
f = json.loads((k / case / 'forensics.json').read_text())
assert f['full_fat_transports_exact'] and f['parent_unchanged']
patterns = {
    'ide_bus_exec_cmd': re.compile(r'ide_bus_exec_cmd IDE exec cmd: bus ([0-9a-f]+); state ([0-9a-f]+); cmd (0x[0-9a-f]+)'),
    'ide_dma_cb': re.compile(r'ide_dma_cb IDEState ([0-9a-f]+); sector_num=(\d+) n=(\d+) cmd=DMA (READ|WRITE|TRIM)'),
    'ide_sector_write': re.compile(r'ide_sector_write sector=(\d+) nsectors=(\d+)'),
    'blk_co_pwritev': re.compile(r'blk_co_pwritev blk ([0-9a-f]+) bs ([0-9a-f]+) offset (\d+) bytes (\d+) flags (0x[0-9a-f]+)'),
    'bdrv_co_pwritev_part': re.compile(r'bdrv_co_pwritev_part bs ([0-9a-f]+) offset (\d+) bytes (\d+) flags (0x[0-9a-f]+)'),
}
counts = collections.Counter()
commands = collections.Counter()
events = []
errors = []
lines = raw.decode('ascii').splitlines()
assert raw.endswith(b'\n'), 'Incomplete trailing trace record'
for line_no, line in enumerate(lines, 1):
    name = line.split(' ', 1)[0]
    counts[name] += 1
    match = patterns.get(name)
    match = match.fullmatch(line) if match else None
    if not match:
        errors.append(dict(line=line_no, text=line[:250]))
        continue
    args = match.groups()
    e = dict(line=line_no, kind=name)
    if name == 'ide_bus_exec_cmd':
        commands[args[2]] += 1
        continue
    if name == 'ide_dma_cb':
        if args[3] != 'WRITE':
            continue
        e.update(offset=int(args[1])*512, bytes=int(args[2])*512, state=args[0])
    elif name == 'ide_sector_write':
        e.update(offset=int(args[0])*512, bytes=int(args[1])*512)
    elif name == 'blk_co_pwritev':
        e.update(offset=int(args[2]), bytes=int(args[3]), blk=args[0], bs=args[1], flags=args[4])
    else:
        e.update(offset=int(args[1]), bytes=int(args[2]), bs=args[0], flags=args[3])
    events.append(e)
assert not errors, errors[:5]
by_line = {e['line']:e for e in events}

def overlap(start, size, event):
    return start < event['offset'] + event['bytes'] and event['offset'] < start + size

def summarize(start, size):
    # Nested bdrv offsets may address QCOW metadata/host files, so they cannot be
    # interpreted as virtual-disk offsets without a matching top-level bs.
    selected = [e for e in events if e['kind'] != 'bdrv_co_pwritev_part' and overlap(start, size, e)]
    top = [e for e in selected if e['kind'] == 'blk_co_pwritev']
    nested = [e for e in events if e['kind'] == 'bdrv_co_pwritev_part'
              and any(e['bs'] == t['bs'] for t in top) and overlap(start, size, e)]
    triplets = []
    for t in top:
        before, after = by_line.get(t['line']-1, {}), by_line.get(t['line']+1, {})
        if (before.get('kind') == 'ide_dma_cb' and after.get('kind') == 'bdrv_co_pwritev_part'
                and before['offset'] == t['offset'] == after['offset']
                and before['bytes'] == t['bytes'] == after['bytes'] and after['bs'] == t['bs']):
            triplets.append(t['line'])
    return dict(offset=start, bytes=size, request_counts=dict(collections.Counter(e['kind'] for e in selected)),
                matching_root_bdrv_entries=len(nested), first_requests=selected[:8], last_requests=selected[-8:],
                adjacent_matching_ide_block_root_triplets=len(triplets),
                request_lines=[e['line'] for e in selected])

files = {}
for name, row in f['files'].items():
    if row.get('absent'):
        files[name] = dict(absent=True)
        continue
    remaining = row['length']
    extents = []
    for cluster in row['chain']:
        size = min(remaining, f['partition']['cluster_size'])
        extents.append(dict(cluster=cluster['cluster'], data=summarize(cluster['byte_offset'], size),
                            allocation=summarize(cluster['fat_byte_offset'], 4)))
        remaining -= size
    assert remaining == 0
    files[name] = dict(cold_sha256=row['sha256'], stale_equals_parent=row['equals_parent_same_clusters'],
                       directory=summarize(row['directory_byte_offset'], 64), extents=extents)
out = dict(case=case, physical_access=False, trace_sha256=hashlib.sha256(raw).hexdigest(), trace_bytes=len(raw),
           line_count=sum(counts.values()), event_counts=dict(counts), command_counts=dict(commands),
           parse_errors=errors, files=files,
           cim_first_cluster=summarize(f['cim_rec']['byte_offset'], f['partition']['cluster_size']),
           cim_fat_entry=summarize(f['cim_rec']['fat_byte_offset'], 4),
           limits='Trace records IDE transfer or block request entry, not completion, success or submitted buffer contents. '
                  'Ranges use independently checked cold metadata. No per-event timestamps; covers the whole emulator lifetime, '
                  'including the dashboard. A request overlap does not establish bytes persisted. Host tracing changes timing.')
(k / case / 'trace-analysis.json').write_text(json.dumps(out, indent=2) + '\n')
selected_lines = set()
for row in files.values():
    for extent in row.get('extents', []):
        for no in extent['data']['request_lines']:
            selected_lines.update(range(max(1,no-1), min(len(lines),no+2)+1))
(k/case/'target-trace.txt').write_text('\n'.join(f'{no}: {lines[no-1]}' for no in sorted(selected_lines))+'\n')
print(json.dumps(dict(events=out['event_counts'], files={n:dict(stale=v.get('stale_equals_parent'),
    data_requests=[x['data']['request_counts'] for x in v.get('extents', [])]) for n,v in files.items()}), indent=2))
