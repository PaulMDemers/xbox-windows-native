"""Review already exported original-control evidence, never reopen the disk."""
import hashlib,json,struct
from pathlib import Path
from cost_oracle import analyze
K=Path(__file__).resolve().parent;P=Path('C:/xwn617/pc001/cold1-002')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False)
try:
 state=read('ntfs-phase1.json');cold=read('ntfs-cold1-002.json');build=read('build001.json')
 assert state['closed'] and state['exit_code']==0 and cold['complete']
 assert not any(state.get(n) for n in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
 assert cold['audit_unchanged'] and cold['source_unchanged'] and cold['normal_shutdown_delta']==1
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives'])
 manifest=json.loads((P/'manifest.json').read_text());logs=P/'files/xwn617'
 for row in build['rows']:
  assert manifest['xwn617-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 log=(logs/'sampler.txt').read_text();trace=(logs/'trace.txt').read_text()
 subjects=[(logs/f'subject{i}.txt').read_text() for i in range(2)]
 host=json.loads(Path('C:/xwn617/pc001/phase1/serial-host.json').read_text())
 (K/'serial-host001.json').write_text(json.dumps(host,indent=2)+'\n')
 (K/'raw-control-logs001.json').write_text(json.dumps(dict(sampler=log,trace=trace,subjects=subjects),indent=2)+'\n')
 result=analyze(log,host,subjects,trace)
 identity=(logs/'identity.bin').read_bytes();assert len(identity)==16
 pid,recorder,lo,hi=struct.unpack('<4I',identity)
 actual=result['cases']['2']['identity'];assert [pid,recorder,lo,hi]==actual[:2]+actual[3:]
 (K/'cost-review001.json').write_text(json.dumps(result,indent=2)+'\n')
 r.update(passed=True,cost=result,identity_file_sha256=sha(logs/'identity.bin'),
  exact_tools=True,normal_shutdown_delta=1,new_system_events=cold['new_system_events'])
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('616 original workload, identities, timing and cold shutdown passed')
