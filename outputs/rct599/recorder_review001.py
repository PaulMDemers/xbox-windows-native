"""Compare the game recorder to the exact qualified597 synthetic implementation."""
import difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct597'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((old/'final001.json').read_text())['passed']
a=(old/'trace002.c').read_text();b=(K/'trace.c').read_text()
diff=list(difflib.unified_diff(a.splitlines(),b.splitlines(),fromfile='qualified597/trace002.c',tofile='discovery599/trace.c',lineterm=''))
unchanged=['readmem','bytewrite','thread','addthread','holdothers','releaseothers','arm','request','ownedbreak','stepped']
for name in unchanged:
 # Every helper before main is byte-identical; compare the complete shared prefix.
 assert a.split('void WINAPI mainCRTStartup(void)')[0]==b.split('void WINAPI mainCRTStartup(void)')[0]
assert 'GetTickCount()-started>360000' in b and 'requests>4096' in b and 'count>10000' in b
assert 'DEBUG_ONLY_THIS_PROCESS' in b and 'TerminateProcess(process,97)' in b
assert 'C:\\\\xwn599-kit\\\\game\\\\RCT.EXE' in b
out=K/'recorder-review001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,qualified_source_sha256=sha(old/'trace002.c'),candidate_sha256=sha(K/'trace.c'),unchanged_helpers=unchanged,diff=diff,review='Only main target/working directory/output, fixed IAT header, bound and exclusive PID receipt differ. The helper owns the debugger process; debugger owns the game. Failed or forced close is not qualification.',limits='Static adaptation check, not game runtime or overhead proof.'),indent=2)+'\n')
print('Shared recorder helpers identical to qualified597')
