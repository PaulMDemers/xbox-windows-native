"""Record actual unsupported-mode refusal; never reinterpret it as a sample run."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cold=json.loads((K/'ntfs-cold1-002.json').read_text());state=json.loads((K/'ntfs-phase1.json').read_text())
assert cold['complete'] and cold['normal_shutdown_delta']==1 and state['closed'] and state['exit_code']==0 and not state['deadline']
assert not any(state.get(k) for k in ('host_quit','host_kill','host_terminate'))
p=Path(cold['private_path'])/'files/xwn445';raw=(p/'runner.txt').read_bytes();r={}
for line in raw.decode('ascii').splitlines():
 k,v=line.split('=',1);assert k not in r and v.isdecimal();r[k]=v
expected=dict(schema='445',mode_original_bits='16',mode_original_width='640',mode_original_height='480',mode_test_status=str(0xfffffffe),completed_cases='0',restart_privilege='1',restart_request='1')
assert all(r.get(k)==v for k,v in expected.items())
assert set(r)==set(expected)|{'pid','start_tick','end_tick'}
assert {f.name for f in p.iterdir()}=={'runner.txt','sprites.exe'}
b=json.loads((K/'build001.json').read_text());assert sha(p/'sprites.exe')==b['rows'][1]['sha256']
pins=json.loads((K/'preflight001.json').read_text())['files']
for name,h in pins.items():assert sha(Path(name))==h,name
(K/'pc001-runner.txt').write_bytes(raw)
result=dict(diagnostic_only=True,mode_request_refused=True,mode_applied=False,sample_cases_executed=0,full_rung04_passed=False,runner=r,normal_restart=True,frozen_dependencies=pins,ordering_failure=json.loads((K/'preflight-ordering-failure001.json').read_text()),scope='CDS_TEST rejected 640x480x32 on pinned Cirrus NT5 driver. Does not qualify any32bit-desktop sample or identify RGB32 failure cause.')
out=K/'runtime-review002.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print('Mode refused before samples; normal restart; diagnostic only.')
