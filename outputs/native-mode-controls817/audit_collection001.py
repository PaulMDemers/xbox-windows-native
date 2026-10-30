"""Audit817 preparation and CR18_linecompare optical evidence locally; never connects or recollects. Preparation evidence and fresh photo001 required; no previous runtime reused."""
import datetime, hashlib, json
from pathlib import Path

K = Path(__file__).resolve().parent
P = Path('C:/xwn817')
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
    for receipt, folder in [('payload008.json', 'payload008'),
                            ('host007.json', 'host007'),
                            ('build002.json', 'build002')]:
        b = read(K / receipt)
        assert b['passed']
        for n, v in b['files'].items():
            assert sha(P / folder / n) == (v['sha256'] if isinstance(v, dict) else v)
        for n, h in b.get('sources', {}).items():
            assert sha(K / n) == h
    for n,h in read(K/'review001.json')['checks'].items():assert sha(K/n)==h
    stage = read(K / 'stage001.json')
    assert stage['completed']
    assert stage['controller_sha256'] == sha(K / 'physical009.py')
    assert stage['staged']['/E/Applications/XWNMode817/default.xbe']['sha256'] == sha(P / 'build002/bin/default.xbe')
    d = rows[-1][1]['data']
    assert d['tool'] == 'xwn-native-mode817' and d['kernel'] == [1, 0, 5838, 1]
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
    assert len(a) == 35 and a[3] == a[7] == 1 and a[8] == 0
    assert 0x200000 <= a[0] < a[0] + a[2] <= 0x2000000 and a[1] <= a[2]
    assert 0x1000000 <= a[4] < a[4] + a[6] <= 0x2000000 and a[5] == a[6] == 40960
    assert a[9] == a[4] and a[10] <= a[9] and a[9] + 40960 <= a[10] + a[11]
    assert a[32] == f['physical'] and a[33] == f['bytes'] and a[34] == f['allocation']
    assert 0x2000000 <= a[32] < a[32] + a[34] <= 0x4000000
    intervals = [(a[0], a[0] + a[2]), (a[4], a[4] + a[6]), (a[32], a[32] + a[34])]
    for i, (lo, hi) in enumerate(intervals):
        assert lo % 4096 == 0
        assert all(hi <= x or y <= lo for x, y in intervals[i + 1:])
        assert hi <= 0x2600000 or lo >= 0x2800000
    starts, ends = a[12:22], a[22:32]
    assert len(set(starts)) == 10
    for lo, end in zip(starts, ends):
        assert lo % 4096 == 0 and end == lo + 4095 and end < 0x4000000
        assert all(end < x or y <= lo for x, y in intervals)
    photo=read(K/'photo001.json');o=read(K/'observation001.json');schema=read(K/'optical-schema001.json');review=read(K/'photo-review001.json')
    assert photo['passed'] and review['passed']
    values=[int(v,16) for v in photo['decoded_rows']]
    assert values==schema['expected_success_rows']==[0x8170000d,0x817]+[0]*8+[56,60,60]
    assert schema['total_masks_required_for_success']==34 and len(schema['omitted_aggregate_masks'])==27
    assert review['fields']==dict(zip(schema['names'],values))
    assert review['bits']==416 and review['adjacent_row_cross_checks']==352
    assert review['offset_samples_per_bit']==5 and review['thresholds_per_sample']==3
    for key,name in [('decoder_sha256','photo_decode001.py'),('decode_sha256','photo001.json'),('schema_sha256','optical-schema001.json'),('reviewer_sha256','photo_review001.py')]:assert review[key]==sha(K/name)
    assert photo['photo_sha256']==review['photo_sha256']==sha(P/'photo001.jpg')
    assert o['user_observation']=='Green, ready'
    ready=read(K/'collection-ready001.json');assert ready['dashboard_confirmed'] and ready['manual_power_cycle_reported_by_standing_workflow']
    assert read(K/'dashboard002.json')['authenticated']
    r.update(passed=True,report_count=9,last_persisted_phase='handoff_armed',private_sources_binaries_reports_exact=True,independent_alias_overlap_check=True,allocation_bytes=40960,alias_pages=10,native_result_persisted=False,native_optical_values=values,native_final_success_code=values[1],native_seven_displayed_cleanup_masks_zero=True,native_mode_controls_forward_mask_zero=True,CR1A_before=56,CR1A_after=60,CR1A_after_CR2D_undo_before_own_undo=60,CR1A_final_restoration_raw_exposed=False,native_other27_cleanup_masks_aggregate_only=schema['omitted_aggregate_masks'],same_value_controls_effective_write_proved=False,pre_arm_cpu=d['pre_arm_cpu'],normal_Windows_shutdown=False,manual_power_cycle=True,reset_basis=ready['basis'])
    r['pins']={n:sha(K/n) for n in ['collection001.json','photo001.json','photo-review001.json','observation001.json','optical-schema001.json','review001.json']}
except BaseException as e:r['failure']=repr(e);raise
finally:
    r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS817 preparation integrity and independent optical evidence; no desktop claim')
