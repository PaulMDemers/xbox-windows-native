"""Reject missing/reordered/failed reset evidence and drawing regressions."""
import hashlib,json
from pathlib import Path
from protocol import validate_log
k=Path(__file__).resolve().parent
p=k.parent/'video-mode-reset/candidate001/artifacts/result.log';original=p.read_bytes();data=original.replace(b'ATTEMPT_ONCE 124 ',b'ATTEMPT_ONCE 131 ').replace(b'DRIVER_REVISION_GEOMETRY 109 ',b'DRIVER_REVISION_GEOMETRY 110 ').replace(b'MODE_DRIVER_AFTER 109 ',b'MODE_DRIVER_AFTER 110 ');text=data.decode('ascii')
assert validate_log(data)['passed'];dest=k/'oracle-tests.json';assert not dest.exists()
mutations={
 'missing_reset':'\n'.join(s for s in text.splitlines() if not s.startswith('MODE_RESET '))+'\n',
 'reset_failed':text.replace('MODE_RESET 0 ','MODE_RESET 4294967295 '),
 'test_failed':text.replace('MODE_TEST 0 ','MODE_TEST 1 '),
 'registry_write':text.replace('MODE_RESET 0 1073741824 0','MODE_RESET 0 1073741825 0'),
 'missing_current_mode':text.replace('MODE_ENUM_END 1 1 1','MODE_ENUM_END 1 1 0'),
 'wrong_after_geometry':text.replace('MODE_AFTER 1024 576 32','MODE_AFTER 640 480 32'),
 'wrong_driver':text.replace('MODE_DRIVER_AFTER 110','MODE_DRIVER_AFTER 108'),
 'omitted_hidden_phase':'\n'.join(s for s in text.splitlines() if s!='CURSOR_PHASE 13 1 0')+'\n',
 'bad_after_reset_pixel':text.replace('PIXELS_BAD_CHANGED 98304 0 ','PIXELS_BAD_CHANGED 98304 1 ',1),
 'truncated':text[:len(text)//2],
 'duplicate_reset':text.replace('MODE_RESET 0 1073741824 0','MODE_RESET 0 1073741824 0\nMODE_RESET 0 1073741824 0'),
}
# Actual enumeration count need not be one.
line=next(s for s in text.splitlines() if s.startswith('MODE_ENUM_END '))
mutations['missing_current_mode']=text.replace(line,line.rsplit(' ',1)[0]+' 0')
rows=[]
for name,value in mutations.items():
 assert value!=text and not validate_log(value.encode())['passed'],name
 rows.append(dict(name=name,rejected=True))
dest.write_text(json.dumps(dict(passed=True,host_only=True,retagged_baseline_for_protocol_test=True,baseline_log_sha256=hashlib.sha256(original).hexdigest(),pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['protocol.py','test-oracle.py']},tests=rows,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
print('Rejected',len(rows),'malformed or failing actual-log variants')
