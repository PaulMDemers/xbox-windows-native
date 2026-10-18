"""Actual power-condition admission and marker checks, modeled records only."""
import importlib.util,json,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('cold534',K/'controller.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ready=dict(ordinal=1,ready=True,power_off_on_reported=True,off_wait_requested_seconds=10)
audit=dict(closed=True,hives_clean=True,ordinary_code_exact=True);cases=[]
m.admit(1,ready);m.admit(2,dict(ready,ordinal=2),audit);cases+=['first_allowed','second_allowed']
for change in [dict(ordinal=1),dict(ready=False),dict(power_off_on_reported=False),dict(off_wait_requested_seconds=0)]:
    bad=dict(ready,ordinal=2);bad.update(change)
    try:m.admit(2,bad,audit)
    except AssertionError:cases.append('reject_ready_'+next(iter(change)))
    else:raise AssertionError(change)
for key in audit:
    try:m.admit(2,dict(ready,ordinal=2),dict(audit,**{key:False}))
    except AssertionError:cases.append('reject_audit_'+key)
    else:raise AssertionError(key)
trace=b'XWN-VID-TRACE01\n'+bytes([51])*4080;assert m.trace_valid(trace)
for i in range(16):
    bad=bytearray(trace);bad[i]^=1;assert not m.trace_valid(bad)
assert not m.trace_valid(trace[:-1]) and not m.trace_valid(trace+b'\0')
r=dict(passed=True,cases=cases,trace_negative_cases=18,used_trace_allowed=True,
       scope='Actual admission/trace validation; modeled records, no console. Single-request primitive and supervisor inherited from532',
       controller_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest())
out=K/'host001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
