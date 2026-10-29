"""Audit808 preparation and CR07_linecompare optical evidence locally; never connects or recollects. Preparation evidence and fresh photo001 required; no previous runtime reused."""
import datetime, hashlib, json
from pathlib import Path

K = Path(__file__).resolve().parent
P = Path('C:/xwn808')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
out = K / 'audit002.json'
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
    assert stage['staged']['/E/Applications/XWNMode808/default.xbe']['sha256'] == sha(P / 'build002/bin/default.xbe')
    d = rows[-1][1]['data']
    assert d['tool'] == 'xwn-native-mode808' and d['kernel'] == [1, 0, 5838, 1]
    assert d['gpu_revision'] == 0xd3 and d['mcp_revision'] == 0xd5
    assert d['preflight_passed'] and d['page_copies_verified'] and d['selectors_restored']
    assert d['allocation_refusal_bits'] == 0 and not d['native_transition']
    assert d['sdk_mode'] == [1280, 720, 32, 60] and d['geometry']['pitch_bytes'] == 5120
    assert dict(d['geometry']['registers'])[0x680830] == 3
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
    photo=read(K/'photo001.json');o=read(K/'observation001.json');schema=read(K/'optical-schema001.json')
    assert schema['total_masks_required_for_success']==31 and len(schema['omitted_aggregate_masks'])==23
    values=[int(v,16) for v in photo['decoded_rows']]
    assert photo['passed'] and len(values)==13 and values[0]==0x8080000d
    assert values[1]==0x808 and values[2:10]==[0]*8
    assert values[10:13]==[62,62,62]
    review=read(K/'photo-review002.json')
    assert review['passed'] and review['fields']==dict(zip(schema['names'],values))
    assert review['bits']==416 and review['adjacent_row_cross_checks']==352
    assert review['offset_samples_per_bit']==5 and review['thresholds_per_sample']==3
    assert review['decoder_sha256']==sha(K/'photo_decode001.py')
    assert review['decode_sha256']==sha(K/'photo001.json')
    assert review['schema_sha256']==sha(K/'optical-schema001.json')
    assert review['reviewer_sha256']==sha(K/'photo_review002.py')
    assert o['user_observation']=='Green' and o['manual_reset_basis']=='standing photo/reset workflow with authenticated dashboard, not a new Ready reply'
    assert photo['photo_sha256']==review['photo_sha256']==sha(P/'photo001.jpg')
    ready=read(K/'collection-ready001.json')
    assert ready['manual_power_cycle_reported_by_standing_workflow'] and ready['dashboard_confirmed'] and not ready['explicit_new_reset_reply']
    r['optical_pins']={n:sha(K/n) for n in ['photo001.json','photo_decode001.py','photo-review002.json','observation001.json','optical-schema001.json']}
    r.update(passed=True,report_count=9,last_persisted_phase='handoff_armed',
      private_sources_binaries_reports_exact=True,independent_alias_overlap_check=True,
      native_result_persisted=False,
      native_forward_raw_status_exposed=False,native_final_success_code=values[1],
      native_CR07_linecompare_before_after_restored=values[10:13],
      native_omitted_raw_masks=schema['omitted_aggregate_masks'],
      native_CR07_linecompare_raw_values_exposed=True,
      same_value_CR02_NVVVALIDSTART_CR07total_write_effect_proved=False,
      native_neighbors_and_selectors_exposed=False,native_prior_individual_restorations_aggregate_only=True,
      native_CR0_CR3_CR4_exposed=False,native_H7_individual_words_exposed=False,
      native_eight_displayed_cleanup_masks_passed=values[2:10]==[0]*8,native_optical_values=values,
      pre_arm_cpu=d['pre_arm_cpu'],normal_shutdown=False,manual_power_cycle=True,reset_basis=ready['basis'],explicit_new_reset_reply=False)

except BaseException as e:
    r['failure'] = repr(e)
    raise
finally:
    r['utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({n:r[n] for n in ['passed','report_count','native_CR07_linecompare_before_after_restored','native_eight_displayed_cleanup_masks_passed','normal_shutdown','manual_power_cycle']}))
