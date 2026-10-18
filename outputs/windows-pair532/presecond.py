"""Require completed first review and corrected trace contract before second launch."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'presecond001.json';assert not out.exists()
assert read(K/'before-review002.json')['passed']
a=read(K/'audit1.json');assert a['closed'] and a['hives_clean'] and a['ordinary_code_exact']
assert a['source_sha256']==read(K/'audit-source-review002.json')['source_sha256']==sha(K/'audit.py')
o=read(K/'observer1.json');assert o['windows_desktop_observed'] and o['at_dashboard'] and not o['manual_reset']
c=read(K/'after1.json');assert c['completed']
trace=Path(c['files']['/E/winnt/system32/xwn-video-trace.bin']['path']).read_bytes()
assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
assert 1<=int.from_bytes(trace[16:20],'little')<=254
assert all(read(K/f'supervisor-{x}.json')['closed'] for x in ['before','launch1','after1'])
r=dict(passed=True,trace_magic_valid=True,trace_records=int.from_bytes(trace[16:20],'little'),
       first_normal_shutdown_delta=a['events']['system']['normal_shutdown_delta'],
       pins={str(K/n):sha(K/n) for n in ['audit1.json','observer1.json','after1.json','before-review002.json','audit-source-review002.json']},
       no_trace_reset=True,no_driver_change=True,second_launch_not_yet_requested=True)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
