"""Pure unchanged-v3 log analysis; incomplete/occluded samples never pass."""
def analyze(log):
    rows=[line.split() for line in (log or '').splitlines()]
    timed=[v for v in rows if v[0]=='TIMING_kind_count_ms']
    coverage=len(timed)==5 and {int(v[1]) for v in timed}==set(range(5)) and all(1<=int(v[2])<=2000 and 0<int(v[3])<=181000 for v in timed)
    return dict(probe_passed=bool(rows) and rows[0]==['XWN_GDI_PROBE_VERSION','3','256','128'] and rows[-1]==['PASS','0','0','0'] and not any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in rows),
        copy_checks_passed=all(['COPY_stage_pass',str(i),'1','0'] in rows for i in range(4)),
        loop_coverage=coverage,timed_loops=timed,
        actual_caps=[v for v in rows if v[0]=='CAP_index_value'],
        actual_modes=[v for v in rows if v[0].startswith('MODE_')])
