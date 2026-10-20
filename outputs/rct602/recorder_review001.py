"""Exact qualified601 core; only owned game main/IAT/bound differ."""
import difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct601';out=K/'recorder-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((old/'final001.json').read_text())['passed']
a=(old/'trace.c').read_text();b=(K/'trace.c').read_text()
assert a.split('void WINAPI mainCRTStartup(void)')[0]==b.split('void WINAPI mainCRTStartup(void)')[0]
assert (old/'calls.h').read_bytes()==(K/'calls.h').read_bytes()
assert 'GetTickCount()-started>360000' in b and 'requests>4096' in b and 'count>10000' in b
assert 'DEBUG_ONLY_THIS_PROCESS' in b and 'C:\\\\xwn602-kit\\\\game\\\\RCT.EXE' in b
out.write_text(json.dumps(dict(passed=True,qualified_trace_sha256=sha(old/'trace.c'),candidate_sha256=sha(K/'trace.c'),
 calls_sha256=sha(K/'calls.h'),diff=list(difflib.unified_diff(a.splitlines(),b.splitlines(),lineterm='')),
 scope='Exact601 helpers and call pairing; main target/path/PID receipt/bound and fixed remote IAT header adapted. Not game runtime or overhead proof.'),indent=2)+'\n')
