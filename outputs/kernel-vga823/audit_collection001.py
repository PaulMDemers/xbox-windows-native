"""Audit retained823 files locally after one collection; never recollect."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn823')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'auditor_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 rows=sorted(c['reports'].items())
 assert [v['data']['phase'] for _,v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','complete_transaction_armed','complete_transaction_returned','restart_requested']
 for name,v in rows:
  p=P/'collection001'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'] and read(p)==v['data']
 for name,h in read(K/'sources001.json').items():assert sha(K/name)==h
 for name,h in read(K/'review001.json')['checks'].items():assert sha(K/name)==h
 build=read(K/'build003.json');assert build['passed']
 for name,v in build['files'].items():assert sha(P/'build003'/name)==v['sha256']
 stage=read(K/'stage001.json');assert stage['completed'] and stage['controller_sha256']==sha(K/'physical.py')
 assert stage['staged']['/E/Applications/XWNMode823/default.xbe']['sha256']==sha(P/'build003/bin/default.xbe')
 assert all(v['data']['kernel_qpc_frequency']==3375000 and v['data']['kernel_qpc_frequency_high']==0 for _,v in rows[1:])
 d=rows[-1][1]['data'];v=d['transaction_words'];assert len(v)==106 and rows[-2][1]['data']['transaction_words']==v
 assert d['tool']=='xwn-native-mode823' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert f['physical']%4096==0 and 0<=f['physical']<0x4000000 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 assert v[102:]==[3,0,0,1], 'First VGA mismatch differs'
 assert v[100:102]==[0x30,0x31], 'Address-write alias not as hypothesized'
 assert d['transaction_phase']==v[0]==7 and d['transaction_error']==d['transaction_return']==v[1]==11
 assert v[2:11]==[1,0,0,720,480,2880,f['physical'],0x83,255]
 assert v[19:25]==[148,148,144,144,3,0], 'Encoder completion differs'
 assert v[36:40]==[0]*4, 'Settle unexpectedly executed'
 assert d['kernel_alias']==f['physical']|0x80000000 and d['kernel_alias_exact']
 flags=d['flags_around_call'];assert flags==[646,134,646] and flags[0]==flags[2] and not flags[1]&0x200
 assert read(K/'dashboard002.json')['authenticated'] and d['complete']
 r.update(passed=True,meaning='Evidence integrity and bounded return; transaction FAILED VGA readback after encoder completion',transaction_passed=False,phase=7,error=11,encoder_attempts=148,interrupt_flags=flags,raw_result=v,automatic_dashboard_return_inferred=True,visual_result_observed=False,normal_windows_shutdown=False,native_mode_proved=False,Windows_support_proved=False)

except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
