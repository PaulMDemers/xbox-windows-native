"""Review cold actual NT5 sample outputs without promoting them to Xbox results."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_sample
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'runtime-review002.json';assert not out.exists()
cold=json.loads((K/'ntfs-cold1-002.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline'] and not any(state.get(n) for n in ['host_quit','host_terminate','host_kill'])
assert cold['complete'] and cold['normal_shutdown_delta']==1 and cold['source_unchanged'] and cold['audit_unchanged']
p=Path(cold['private_path'])/'files/xwn437'
assert sha(p/'ladder.exe')=='09d355d8e55081433b62f94a2203cfa56bb23c4e6181f07f9b5087c7b6f3d050'
def fields_only(raw):
 assert 0<len(raw)<=32768
 fields={}
 for line in raw.decode('ascii').splitlines():
  key,sep,value=line.partition('=');assert sep and key and value and key not in fields
  fields[key]=value
 return fields
runner=fields_only((p/'runner.txt').read_bytes())
expected={'schema','pid','start_tick','completed_cases','end_tick','restart_privilege','restart_request'}|{f'case{i}_{s}' for i in range(6) for s in ['start_tick','pid','wait','exit']}
assert set(runner)==expected and all(v.isdecimal() and 0<=int(v)<=0xffffffff for v in runner.values())
assert runner['schema']=='437' and runner['completed_cases']=='6' and runner['restart_privilege']=='1' and runner['restart_request']=='1'
record=dict(scope='Actual Windows 2000 SP4 PC/Cirrus control, 64 MiB; no Xbox or GPU qualification',rows=[],runner=runner,all_allowed_cases_passed=False)
for i,name in enumerate(['r00','r01d','r01s','r01h','r02d','r02s']):
 assert runner[f'case{i}_wait']=='0'
 exitcode=(p/(name+'.exit')).read_text().strip();assert exitcode==runner[f'case{i}_exit']
 fields=fields_only((p/(name+'.txt')).read_bytes())
 assert [fields[n] for n in ['os.api.major','os.api.minor','os.api.build']]==['5','0','2195']
 row=dict(name=name,process_exit=int(exitcode),fields=fields)
 try:row['review']=graphics_sample.review(p/name,p/(name+'.exit'))
 except Exception as exc:row['review_failure']=str(exc)
 for f in p.glob(name+'*'):
  if f.suffix in ['.txt','.exit']:(K/('pc001-'+f.name)).write_bytes(f.read_bytes())
 record['rows'].append(row)
(K/'pc001-runner.txt').write_bytes((p/'runner.txt').read_bytes())
record['all_allowed_cases_passed']=all('review' in r for r in record['rows'])
record['files']={str(f):sha(f) for f in p.iterdir() if f.is_file()}
record['frozen_dependencies']={}
for f,h in json.loads((K/'preflight001.json').read_text())['files'].items():
 assert sha(Path(f))==h,f;record['frozen_dependencies'][f]=h
out.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'all_allowed_cases_passed':record['all_allowed_cases_passed'],'rows':[{n:r[n] for n in ['name','process_exit','review_failure'] if n in r} for r in record['rows']]}))
