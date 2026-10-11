"""Actual closed positive/negative logs and finite malformed telemetry guards."""
import importlib.util,json
from pathlib import Path
from diagnostic import decode
k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original219',k.parent/'video-boot-layout219/runner_analysis.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
positive=(k.parent/'worker-barrier247/preserve001/artifacts/wizard201.log').read_bytes()
negative=(k.parent/'worker-barrier248/preserve001/artifacts/wizard201.log').read_bytes()
assert p.helper(decode(positive)[1],1)['passed']
try:p.helper(decode(negative)[1],1)
except (AssertionError,ValueError):pass
else:raise AssertionError('Old timeout promoted')
sample=b'WAIT_SAMPLE249 15 840 65654\r\nFG_WAIT249 908 70000 900\r\nGUI_WAIT249_OWNER 840 844 0\r\nGUI_WAIT249_ACTIVE 0 65654 65656\r\nGUI_WAIT249_CAPTURE 0 0 0\r\nWAIT_FG249 908 70000 900\r\nWAIT_WINDOW249 1 1 1\r\nWAIT_TEXT249 1 1 0\r\nWAIT_TITLE249 70000 7 57656c636f6d65\r\nWAIT_CLASS249 70000 0 \r\nWAIT_OWNER249 908 1 258\r\nWAIT_CREATION249 908 1 2\r\nWAIT_COMMAND249 908 11 77656c636f6d652e65786500\r\nWAIT_END249 30 840 65654\r\n'
raw=negative.replace(b'CANCEL_ACTIVE_WAIT 840 65654 0\r\n',b'CANCEL_ACTIVE_WAIT 840 65654 0\r\n'+sample,1)
d,project=decode(raw);assert project==negative and d['foreground_refusal_observed'] and len(d['samples'])==1
bad=[raw.replace(b'WAIT_END249 30',b'WAIT_END249 1'),raw.replace(b'WAIT_TEXT249',b'WAIT_UNKNOWN249'),raw.replace(b' 7 57656c',b' 8 57656c'),raw.replace(b'WAIT_END249 30 840 65654\r\n',b''),raw.replace(b'WAIT_CLASS249 70000',b'WAIT_CLASS249 70001'),raw+b'\xff']
for v in bad:
 try:decode(v)
 except (AssertionError,ValueError,UnicodeError):pass
 else:raise AssertionError('Malformed diagnostic accepted')
dest=k/'diagnostic-test001.json';assert not dest.exists();dest.write_text(json.dumps(dict(passed=True,actual_closed_logs=2,synthetic_refused_sample=1,negative_guards=len(bad),physical_access=False),indent=2)+'\n');print('249 diagnostic grammar/projection guards PASS')
