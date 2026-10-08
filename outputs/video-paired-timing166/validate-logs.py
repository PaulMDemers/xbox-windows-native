"""Exercise qualification failures using real collected v3 logs, not generated passes."""
import json
from pathlib import Path
from sample_analysis import analyze
k=Path(__file__).resolve().parent
log=(k.parent/'video-hardware-trial164/artifacts/physical/after-gdi-baseline.txt').read_bytes().decode('ascii')
good=analyze(log);assert good['probe_passed'] and good['copy_checks_passed'] and good['loop_coverage']
checks=0
for bad in [None, '', log.replace('PASS 0 0 0','FAIL 1 0 0'), log+'MISMATCH_stage_x_y 1 2 3\r\n',
            log.replace('COPY_stage_pass 2 1 0','COPY_stage_pass 2 0 0'),
            '\r\n'.join(v for v in log.splitlines() if not v.startswith('TIMING_kind_count_ms 4 ')),
            log.replace('TIMING_kind_count_ms 4 343 1500','TIMING_kind_count_ms 3 343 1500'),
            log.replace('TIMING_kind_count_ms 4 343 1500','TIMING_kind_count_ms 4 0 1500')]:
    a=analyze(bad);assert not(a['probe_passed'] and a['copy_checks_passed'] and a['loop_coverage']);checks+=1
(k/'log-gate-tests.json').write_bytes((json.dumps(dict(passed=True,real_pass_checked=True,negative_cases=checks),indent=2)+'\n').encode('utf-8'))
print('Real-log success and eight incomplete/corrupt log gates verified')
