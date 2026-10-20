"""Compare cached qualified intervals, without reopening either runtime."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'comparison001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=K.parent/'rct615';a=json.loads((old/'cost-review001.json').read_text())
b=json.loads((K/'cost-review001.json').read_text());assert a['passed'] and b['passed']
assert json.loads((old/'final001.json').read_text())['closed']
assert json.loads((K/'review001.json').read_text())['passed']
for name in ['input.h','park_reference.h','load_dialog002.h','game_capture.h']:
 assert (K/name).read_text()==(old/name).read_text().replace('xwn615','xwn618').replace('XWN615','XWN618'),name
oldlog=json.loads((old/'raw-counter-logs001.json').read_text())['cost']
newlog=json.loads((K/'raw-counter-logs001.json').read_text())['cost']
def role(log,prefix,sample):
 rows={}
 for line in log.splitlines():
  p=line.split()
  if p[0] in [prefix+'_START',prefix+'_END',sample]:
   rows.setdefault(p[0],[]).append(dict(tick=int(p[4]),k=int(p[5],16),u=int(p[6],16),
    ws=int(p[7]),page=int(p[9])))
 start,end=[rows[prefix+'_'+v][0] for v in ['START','END']]
 elapsed=(end['tick']-start['tick'])/1000
 kernel=(end['k']-start['k'])/1e7;user=(end['u']-start['u'])/1e7
 assert elapsed>0 and kernel>=0 and user>=0
 r=dict(elapsed_seconds=elapsed,kernel_seconds=kernel,user_seconds=user,
  cpu_seconds=kernel+user,cpu_fraction=(kernel+user)/elapsed)
 if sample in rows:
  r.update(working_set_range=[min(v['ws'] for v in rows[sample]),max(v['ws'] for v in rows[sample])],
   pagefile_usage_range=[min(v['page'] for v in rows[sample]),max(v['page'] for v in rows[sample])])
 return r
pristine=role(oldlog,'GAME','SAMPLE')
recorded={r:role(newlog,r,r+'_SAMPLE') for r in ['SUBJECT','TRACER','OBSERVER']}
assert pristine['cpu_seconds']==a['game']['cpu_seconds']
assert recorded['SUBJECT']['cpu_seconds']==b['cases']['1']['cpu_seconds']
out.write_text(json.dumps(dict(passed=True,baseline615=pristine,recorded618=recorded,
 host_seconds=[a['game']['host_seconds'],b['cases']['1']['host_seconds']],
 timing=b['timing'],sources={str(p):sha(p) for p in [old/'cost-review001.json',K/'cost-review001.json']},
 limits=['One interval per condition, PC emulator only.','Finite32-call-pair policy then capped entry handling, not continuous full tracing.',
 'CPU-time distribution is not game FPS, useful simulation work or an acceleration result.',
 'Working set and PagefileUsage counters do not measure disk paging traffic.',
 'Game keeps running during log output after end markers; exclude those hits.']),indent=2)+'\n')
