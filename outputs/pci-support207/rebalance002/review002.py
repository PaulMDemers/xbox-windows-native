"""Compare fresh skip/allow/veto cases using exact binary pins, trace and timed events."""
import ast, collections, datetime, hashlib, json, struct
from pathlib import Path
k = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
build = read(k / 'build001.json')
for row in build['sources']: assert sha(k / row['name']) == row['sha256'], row['name']
for row in build['files']: assert sha(k / 'artifacts/build001' / row['name']) == row['sha256'], row['name']
assert (k / 'compiler001.txt').read_text(encoding='utf-8-sig').split()[0] == '83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5'
assert read(k / 'build-review001.json')['passed']
assert sha(k / 'artifacts/build001/xwnrsc.sys') == '3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92'
assert sha(k / 'xwnrsc.inf') == sha(k.parent / 'stop001/xwnrsc.inf')
assert sha(k / 'e_allocation.py') == sha(k.parent / 'stop001/e_allocation.py')
cases = []
clock = read(k / 'clock-registry001.json')
bias = clock['values']['\\ControlSet001\\Control\\TimeZoneInformation']['ActiveTimeBias']['decoded']
assert bias == 240
for mode, arm in enumerate(('skip', 'allow', 'veto')):
    d = k / (arm + '001')
    assert sha(d / 'artifacts/before-system') == clock['sha256']
    a, p, r, f, t = [read(d / name) for name in ('audit.json', 'pnp-review.json', 'run.json', 'fixture.json', 'resource-trace.json')]
    assert r['closed'] and r['source_unchanged'] and not r.get('unexpected_exit')
    assert a['integrity_passed'] and p['qualified_resource_only_installation'] and p['lifecycle_completed'] and p['cancel_remove_qualified'] and p['hal_probe_passed']
    assert f['hal_sha256'] == '234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255'
    lines = p['log'].splitlines()
    assert 'rebalance_mode=' + str(mode) in lines
    expected = ('REBALANCE_SKIP_CONTROL', 'REBALANCE_STOP_RECOVERED', 'REBALANCE_CANCEL_RECOVERED')[mode]
    assert lines.count(expected) == 1
    markers = []
    for i, line in enumerate(lines):
        if line.startswith('mark='):
            assert lines[i+1].startswith('utc_filetime_hi=') and lines[i+2].startswith('utc_filetime_lo=')
            ft = (int(lines[i+1].split('=')[1]) << 32) | int(lines[i+2].split('=')[1])
            unix = (ft - 116444736000000000) / 10000000
            markers.append(dict(name=line[5:], unix=unix, filetime_utc=datetime.datetime.fromtimestamp(unix, datetime.timezone.utc).isoformat(), raw_filetime=ft, bias_adjusted_epoch=unix-bias*60, uptime_ms=int(lines[i+3].split('=')[1])))
    by = {m['name']: m for m in markers}
    minors = collections.Counter(x['profile'] for x in t['records'] if x['stage'] == 5)
    for minor, count in zip((5, 4, 6), ((0,0,0), (1,1,0), (1,0,1))[mode]): assert minors[minor] == count
    segments = []
    for x in t['records']:
        if x['sequence'] == 1: segments.append([])
        assert x['sequence'] == len(segments[-1]) + 1
        segments[-1].append(x)
    assert all(len(s) < 64 for s in segments)
    events = []
    for e in a['warnings_errors']:
        row = dict(source=e['source'], event_id=e['event_id'], record=e['record'], generated_unix=e['generated_unix'], seconds_from_rebalance_begin=e['generated_unix']-by['rebalance_begin']['unix'], strings=e['strings'])
        if e['source'] in ('Kbdclass', 'Mouclass'):
            data = bytes.fromhex(e['data_hex'])
            row.update(major_function=data[0], error_code=hex(struct.unpack_from('<I', data, 12)[0]), unique_error_value=hex(struct.unpack_from('<I', data, 16)[0]), final_status=hex(struct.unpack_from('<I', data, 20)[0]))
        events.append(row)
    host_start=datetime.datetime.fromisoformat(r['launch_requested_utc']).timestamp();host_end=datetime.datetime.fromisoformat(r['closed_utc']).timestamp()
    assert all(host_start <= m['bias_adjusted_epoch'] <= host_end for m in markers)
    for e in events:
        if e['source'] in ('Kbdclass','Mouclass'):
            assert 0 <= e['seconds_from_rebalance_begin'] <= by['rebalance_end']['unix']-by['rebalance_begin']['unix']
    cases.append(dict(arm=arm, lifecycle_passed=True, integrity_passed=True, marks=markers, pnp_minor_counts=dict(minors), trace_load_lengths=list(map(len, segments)), events=events, counts=[dict(source=s,event_id=i,count=c) for (s,i),c in collections.Counter((x['source'],x['event_id']) for x in events).items()], closed_utc=r['closed_utc'], normal_restart_qualified=p['normal_restart_qualified'], pending_install=p['restart_held_pending_setup'], evidence_sha256={name:sha(d/name) for name in ('audit.json','pnp-review.json','run.json','fixture.json','resource-trace.json')}))
all_fixtures = [read(k/(x+'001/fixture.json')) for x in ('skip','allow','veto')]
different = [n for n in all_fixtures[0]['files'] if len({f['files'][n] for f in all_fixtures}) != 1]
assert len(different) == 1 and 'startup' in different[0].lower()
for mode, arm in enumerate(('skip','allow','veto')):
    cmd=(k/(arm+'001/artifacts/startup.cmd')).read_bytes().replace(b'XWN_REBALANCE_MODE='+str(mode).encode(), b'XWN_REBALANCE_MODE=0')
    assert cmd == (k/'skip001/artifacts/startup.cmd').read_bytes()
for p in k.glob('*.py'): ast.parse(p.read_text(), filename=str(p))
result=dict(evidence_review_passed=True, physical_access=False, identical_driver_hal_installer_and_probe=True, fixture_file_hash_difference=different, only_startup_arm_selector_differs=True, cases=cases, whole_boot_qualified=False, guest_relative_clock_correlation_passed=True, absolute_guest_host_clock_alignment_qualified=False, guest_active_bias_minutes=bias, clock_note='Raw FILETIME-derived epoch and event-log epoch agree. Both guest clocks display four hours ahead of host; subtracting frozen ActiveTimeBias places all helper marks inside the host run interval. Relative guest timing uses raw epochs with no timezone subtraction. Absolute guest clock accuracy is not qualified. Original mistaken host review is preserved in comparison001.json and review-correction001.json.', limits='One fresh case per arm. Diagnostic association does not identify the failing input-port owner or the packet source of an address conflict. No functional input/network, SMBus transaction, terminal takeover, normal restart, repeated-boot or physical qualification.')
dest=k/'comparison002.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({x['arm']:dict(counts=x['counts'], marks=x['marks'], events=x['events']) for x in cases},indent=2))
