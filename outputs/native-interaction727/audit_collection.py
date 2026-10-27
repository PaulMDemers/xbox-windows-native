"""Audit retained727 preparation files locally; never connects or recollects."""
import datetime, hashlib, json
from pathlib import Path

K = Path(__file__).resolve().parent
P = Path('C:/xwn727')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
out = K / 'audit001.json'
assert not out.exists()
r = {'passed': False, 'auditor_sha256': sha(Path(__file__)),
     'kernel_preparation_only': True, 'physical_access': False}
try:
    c = read(K / 'collection001.json')
    assert c['completed'] and c['unrelated_directory_entries_unchanged']
    rows = sorted(c['reports'].items())
    expected = ['start', 'before_kernel_mode', 'allocation_checked',
                'kernel_context_captured', 'before_allocations',
                'after_allocations', 'native_page_ready', 'pattern_submitted',
                'handoff_armed']
    assert len(rows) == 9
    assert [v['data']['phase'] for _, v in rows] == expected
    for n, v in rows:
        p = P / 'collection001' / n
        assert p.stat().st_size == v['bytes'] and sha(p) == v['sha256']
        assert read(p) == v['data']
    for n, h in read(K / 'sources001.json')['files'].items():
        assert sha(K / n) == h, n
    for receipt, folder in [('payload001.json', 'payload001'),
                            ('host002.json', 'host002'),
                            ('build001.json', 'build001')]:
        b = read(K / receipt)
        assert b['passed']
        for n, v in b['files'].items():
            assert sha(P / folder / n) == (v['sha256'] if isinstance(v, dict) else v)
        for n, h in b.get('sources', {}).items():
            assert sha(K / n) == h
    stage = read(K / 'stage001.json')
    assert stage['completed']
    assert stage['controller_sha256'] == sha(K / 'physical.py')
    assert stage['staged']['/E/Applications/XWNMode727/default.xbe']['sha256'] == sha(P / 'build001/bin/default.xbe')
    d = rows[-1][1]['data']
    assert d['tool'] == 'xwn-native-mode727' and d['kernel'] == [1, 0, 5838, 1]
    assert d['gpu_revision'] == 0xd3 and d['mcp_revision'] == 0xd5
    assert d['preflight_passed'] and d['page_copies_verified'] and d['selectors_restored']
    assert d['allocation_refusal_bits'] == 0 and not d['native_transition']
    assert d['sdk_mode'] == [1280, 720, 32, 60] and d['geometry']['pitch_bytes'] == 5120
    assert dict(d['geometry']['registers'])[0x680630] == 3
    f = d['framebuffer']
    assert f['admitted'] and f['contiguous'] and f['page_checks'] == 900
    assert f['bytes'] == 3686400 and f['first_bad_offset'] == 0xffffffff
    assert f['scanout'] == f['physical'] and not f['native_reserved_overlap']
    a = d['allocation_plan_words']
    assert len(a) == 31 and a[3] == a[7] == 1 and a[8] == 0
    assert 0x200000 <= a[0] < a[0] + a[2] <= 0x2000000 and a[1] <= a[2]
    assert 0x1000000 <= a[4] < a[4] + a[6] <= 0x2000000 and a[5] == a[6] == 32768
    assert a[9] == a[4] and a[10] <= a[9] and a[9] + 32768 <= a[10] + a[11]
    assert a[28] == f['physical'] and a[29] == f['bytes'] and a[30] == f['allocation']
    assert 0x2000000 <= a[28] < a[28] + a[30] <= 0x4000000
    intervals = [(a[0], a[0] + a[2]), (a[4], a[4] + a[6]), (a[28], a[28] + a[30])]
    for i, (lo, hi) in enumerate(intervals):
        assert lo % 4096 == 0
        assert all(hi <= x or y <= lo for x, y in intervals[i + 1:])
        assert hi <= 0x2600000 or lo >= 0x2800000
    starts, ends = a[12:20], a[20:28]
    assert len(set(starts)) == 8
    for lo, end in zip(starts, ends):
        assert lo % 4096 == 0 and end == lo + 4095 and end < 0x4000000
        assert all(end < x or y <= lo for x, y in intervals)
    prior=read(K.parent/'native-630726'/'collection001.json')
    old=next(v['data'] for v in prior['reports'].values() if v['data']['phase']=='handoff_armed')
    comparisons={n:old[n]==d[n] for n in ['pci_kernel_reads','crtc_kernel_reads','sequencer_kernel_reads','allocation_plan_words','geometry']}
    photo=read(K/'photo001.json');o=read(K/'observation001.json');schema=read(K/'optical-schema001.json')
    expected=[0x7270000d,4,5,0x727,0x10102,0x30085,0x20085,0x50005,0x30085,0x30085,0x30085,0,0x1022007]
    assert photo['passed'] and [int(v,16) for v in photo['decoded_rows']]==expected
    assert o['decoded_values']==dict(zip(schema['names'],expected))
    assert o['photo_sha256']==photo['photo_sha256']==sha(P/'photo001.jpg')
    r['optical_pins']={n:sha(K/n) for n in ['photo001.json','photo_decode001.py','observation001.json','optical-schema001.json']}
    r.update(passed=True,report_count=9,last_persisted_phase='handoff_armed',
      private_sources_binaries_reports_exact=True,independent_alias_overlap_check=True,
      comparison_to_closed726_preparation=comparisons,native_result_persisted=False,
      native_test_passed=True,native_optical_result='Minimal630/CR1b sequence completes; direct/indexedCR1b05 after one05 write;85 after6303 restore/output/late. Zero changes in32 late pairs. Reproduces observed transition without other prefix writes, not fullmode or semantics proof',
      pre_arm_cpu=d['pre_arm_cpu'],normal_shutdown=False,manual_power_cycle=True)
except BaseException as e:
    r['failure'] = repr(e)
    raise
finally:
    r['utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
