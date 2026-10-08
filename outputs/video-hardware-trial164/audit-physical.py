"""Audit the preserved physical drawing diagnostic; no console access or promotion."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
art = k / 'artifacts/physical'
dest = k / 'physical-audit.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
r = read(k / 'physical.json')
assert r.get('collected_utc') and r['baseline_restored'] and not r['startup_enabled']
result = dict(scope=__doc__, physical_result=True, strict_qualification_passed=False,
              release_qualified=False, performance_qualified=False, new_events={})
result['preserved_files_exact'] = all(row is None or sha((ws / row['path']).read_bytes()) == row['sha256'] for row in r['after'].values())
result['event_history_preserved'] = True
for label, filename in [('system', 'sysevent.evt'), ('application', 'appevent.evt')]:
    pair = []
    for phase in ['before', 'after']:
        output = k / (phase+'-physical-'+label+'-events.json')
        assert not output.exists()
        subprocess.run([sys.executable, str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),
                        str(art/(phase+'-'+filename)), '--output', str(output)], check=True, stdout=subprocess.DEVNULL)
        pair.append(read(output)['records'])
    before, after = pair
    by = {v['record']: v for v in after}
    result['event_history_preserved'] &= all(by.get(v['record']) == v for v in before)
    boundary = max((v['record'] for v in before), default=0)
    result['new_events'][label] = [v for v in after if v['record'] > boundary]
result['warnings_errors'] = [v for group in result['new_events'].values() for v in group if v['type'] in [1, 2]]
log = '' if r['after']['gdi-baseline.txt'] is None else (art/'after-gdi-baseline.txt').read_bytes().decode('ascii')
attempt = '' if r['after']['attempt.log'] is None else (art/'after-attempt.log').read_bytes().decode('ascii')
rows = [line.split() for line in log.splitlines()]
result['probe_log'] = log
result['runner_log'] = attempt
result['probe_passed'] = bool(rows) and rows[0] == ['XWN_GDI_PROBE_VERSION','3','256','128'] and rows[-1] == ['PASS','0','0','0'] and not any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in rows)
result['pixel_checks_passed'] = all(['COPY_stage_pass', str(i), '1', '0'] in rows for i in range(4))
result['timed_loops'] = [v for v in rows if v[0] == 'TIMING_kind_count_ms']
result['loop_coverage'] = len(result['timed_loops']) == 5 and {int(v[1]) for v in result['timed_loops']} == set(range(5)) and all(1 <= int(v[2]) <= 2000 for v in result['timed_loops'])
result['actual_caps'] = [v for v in rows if v[0] == 'CAP_index_value']
result['actual_modes'] = [v for v in rows if v[0].startswith('MODE_')]
result['normal_restart_requested'] = attempt.splitlines() == ['ATTEMPT_ONCE','REPLAY_EXIT_ZERO','NORMAL_RESTART_REQUEST']
result['normal_shutdown_count'] = sum(v['source'] == 'EventLog' and v['event_id'] == 6006 for v in result['new_events']['system'])
result['dashboard_return'] = read(k/'physical-return.json')['dashboard_return']
result['deployed_payloads_exact'] = all(r['after'][row['target'].rsplit('/',1)[1]]['sha256'] == row['sha256'] for row in read(ws/'outputs/video-hardware-candidate158/package-review.json')['candidate'])
trace = (art/'after-trace.bin').read_bytes()
assert len(trace) == 4096 and trace[:16] == b'XWN-VID-TRACE01\n'
count, dropped = struct.unpack_from('<II', trace, 16)
assert count <= 254
result['trace_records'] = count
result['trace_dropped'] = dropped
result['shared_events'] = [list(struct.unpack_from('<4I', trace, 32+i*16)) for i in range(count) if struct.unpack_from('<I', trace, 32+i*16)[0] in [0x30,0x31,0x32]]
acquires = [v for v in result['shared_events'] if v[0] == 0x30]
result['shared_acquire_success'] = bool(acquires) and dropped == 0 and all(v[1] == 0 and v[2] >= 0x80000000 and v[2] % 4096 == 0 and v[3] > 0 for v in acquires) and all(v[1] == 0 for v in result['shared_events'])
result['workload_passed'] = result['probe_passed'] and result['pixel_checks_passed'] and result['loop_coverage'] and result['normal_restart_requested'] and result['normal_shutdown_count'] == 1 and result['dashboard_return']
result['strict_events_passed'] = result['event_history_preserved'] and not result['warnings_errors'] and not result['new_events']['application'] and not any(v['source'] == 'Application Popup' for v in result['new_events']['system'])
result['limits'] = 'Scoped drawing diagnostic only. No full physical allocation or all-file audit, no hardware latency qualification, no new mode qualification. Original display and SYSTEM restored after collection. Existing errors remain strict failures.'
dest.write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps({v: result[v] for v in ['workload_passed','pixel_checks_passed','shared_acquire_success','strict_events_passed','warnings_errors','actual_caps']}, indent=2))
