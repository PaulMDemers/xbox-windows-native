"""Reject truncated logs, lost data, leftover copies and shortened physical duration."""
import json
from pathlib import Path
from workload import verify,SIZES
k=Path(__file__).resolve().parent
rehearsal=json.loads((k/'rehearsal/audit.json').read_text())['workload']
scribble=(k/'artifacts/scribble.bmp').read_bytes()
files={f'{kind}{i:02}.bin':bytes((v*13+i*17+round*29)&255 for v in range(size)) for kind,round in [('input',0),('output',15)] for i,size in enumerate(SIZES)}
files.update({f'match{i:02}.bmp':scribble for i in range(16)})
files.update({'result.log':rehearsal['log'].encode(),'matched.log':rehearsal['matched_log'].encode()})
assert verify(files.get,scribble,4000)['passed']
tests={}
def reject(name,changes,interval=4000):
    data=dict(files);data.update(changes)
    tests[name]=not verify(data.get,scribble,interval)['passed'];assert tests[name]
reject('wrong_final_file',{'output16.bin':b'wrong'})
reject('missing_final_file',{'match15.bmp':None})
reject('leftover_copy',{'copy00.bin':b''})
reject('truncated_completion',{'result.log':files['result.log'].replace(b'NORMAL_RESTART_REQUEST 0 0 0\r\n',b'')})
reject('missing_replay_case',{'matched.log':b'PASS 16 0 0 0\r\n'})
reject('rehearsal_cannot_qualify_physical',{},60000)
(k/'verifier-tests.json').write_text(json.dumps(dict(scope=__doc__,rehearsal_replay_accepted=True,rejections=tests,passed=all(tests.values())),indent=2)+'\n')
print('Verifier negative cases passed:',len(tests))
