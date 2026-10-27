"""Audit retained721 kernel-context files locally; never connects or recollects."""
import datetime, hashlib, json
from pathlib import Path

K = Path(__file__).resolve().parent
P = Path('C:/xwn721')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
out = K / 'audit001.json'
assert not out.exists()
r = {'passed': False, 'auditor_sha256': sha(Path(__file__)),
     'kernel_preparation_only': False, 'physical_access': False}
try:
    c = read(K / 'collection001.json')
    assert c['completed'] and c['unrelated_directory_entries_unchanged']
    rows = sorted(c['reports'].items())
    expected = ['start','before_kernel_mode','allocation_checked','kernel_context_captured',
                'write_control_armed','write_control_returned','restart_requested']
    assert len(rows)==7 and [v['data']['phase'] for _,v in rows]==expected
    for n, v in rows:
        p = P / 'collection001' / n
        assert p.stat().st_size == v['bytes'] and sha(p) == v['sha256']
        assert read(p) == v['data']
    for n, h in read(K / 'sources001.json').items():
        assert sha(K / n) == h, n
    b=read(K/'build001.json');assert b['passed']
    for n,v in b['files'].items():assert sha(P/'build001'/n)==v['sha256']
    for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==b['files'][n]['sha256']
    model=read(K/'model001.json');assert model['passed'] and model['case_count']==916
    assert model['object_sha256']==sha(P/'build001/probe.obj')
    for check in read(K/'link-review002.json')['checks']:assert check['sha256']==sha(P/'build001'/check['image'])
    stage = read(K / 'stage001.json')
    assert stage['completed']
    assert stage['controller_sha256'] == sha(K / 'physical.py')
    assert stage['staged']['/E/Applications/XWNMode721/default.xbe']['sha256'] == sha(P / 'build001/bin/default.xbe')
    d = rows[-1][1]['data']
    assert d['tool'] == 'xwn-native-mode721' and d['kernel'] == [1, 0, 5838, 1]
    assert d['gpu_revision'] == 0xd3 and d['mcp_revision'] == 0xd5
    assert d['selectors_restored'] and not d['native_transition'] and not d['native_handoff_performed']
    assert d['sdk_mode'] == [1280, 720, 32, 60] and d['geometry']['pitch_bytes'] == 5120
    assert dict(d['geometry']['registers'])[0x680630] == 3
    f = d['framebuffer']
    assert f['admitted'] and f['contiguous'] and f['page_checks'] == 900
    assert f['bytes'] == 3686400 and f['first_bad_offset'] == 0xffffffff
    assert f['scanout'] == f['physical'] and not f['native_reserved_overlap']
    prior=read(K.parent/'native-mode720/collection001.json')
    old=next(v['data'] for v in prior['reports'].values() if v['data']['phase']=='handoff_armed')
    comparisons={n:old[n]==d[n] for n in ['pci_kernel_reads','crtc_kernel_reads','sequencer_kernel_reads','geometry']}
    assert all(comparisons.values())
    v=d['kernel_write_control_words'];assert len(v)==24
    assert rows[-2][1]['data']['kernel_write_control_words']==v
    assert v==[0x7218,1,0x85,1,3,0x85,0x85,5,5,5,0x28,1,
               0x282,0x82,0x282,0x80010031,0xf000,0x610,9,9,0x1b,0x1b,1,1]
    assert v[12]==v[14] and not(v[13]&0x200)
    assert v[15]&0x80000001==0x80000001 and not(v[17]&0x20)
    assert read(K/'observation001.json')['top_bar']=='orange'
    assert rows[-1][1]['data']['complete']
    r.update(passed=True,report_count=7,preparation_pins_exact=True,
             last_persisted_phase='restart_requested',kernel_control_passed=False,
             kernel_postwrite_persisted=True,raw_values=dict(zip(read(K/'schema001.json')['words'],v)),
             comparison_to720_preparation=comparisons,
             interpretation='Mismatch reproduced with kernel paging context retained; direct05 before index reselection, selected05, restored05. Native handoff and index reselection not necessary in this control. Bit7 semantics remain unknown.',
             automatic_dashboard_return=True,normal_windows_shutdown=False,manual_power_cycle=False,
             native_handoff=False)
except BaseException as e:
    r['failure'] = repr(e)
    raise
finally:
    r['utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    out.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
