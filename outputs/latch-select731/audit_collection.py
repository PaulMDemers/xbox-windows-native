"""Audit retained731 files locally after one collection; never recollect."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn731')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'auditor_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 rows=sorted(c['reports'].items())
 assert [v['data']['phase'] for _,v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','read_plane_control_armed','read_plane_control_returned','restart_requested']
 for name,v in rows:
  p=P/'collection001'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'] and read(p)==v['data']
 for name,h in read(K/'sources001.json').items():assert sha(K/name)==h
 for name,h in read(K/'review001.json')['checks'].items():assert sha(K/name)==h
 build=read(K/'build001.json');assert build['passed']
 for name,v in build['files'].items():assert sha(P/'build001'/name)==v['sha256']
 stage=read(K/'stage001.json');assert stage['completed'] and stage['controller_sha256']==sha(K/'physical.py')
 assert stage['staged']['/E/Applications/XWNMode731/default.xbe']['sha256']==sha(P/'build001/bin/default.xbe')
 d=rows[-1][1]['data'];v=d['kernel_sample_words'];assert len(v)==43 and rows[-2][1]['data']['kernel_sample_words']==v
 assert d['tool']=='xwn-native-mode731' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert f['physical']%4096==0 and 0<=f['physical']<0x4000000 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 assert v[1]==v[3] and not v[2]&0x200 and v[4]&0x80000001==0x80000001 and not v[6]&0x20
 assert v[0] in [0x731,0x7311,0x7312,0x7313,0x7315,0x7316]
 assert 0<=v[21]<=5 and 0<=v[22]<=4
 observation=read(K/'observation001.json')
 expected='green' if v[0]==0x731 else 'orange' if v[0] in [0x7313,0x7315] else 'red'
 assert observation['top_bar']==expected and observation['automatic_return_observed'] and not observation['manual_reset']
 assert d['complete'] and all(not row['data']['complete'] for _,row in rows[:-1])
 if v[0]==0x731:
  assert v[19:23]==[1,1,5,4] and v[23:27]==v[27:31]==[0,1,2,3]
  assert all(v[a]==v[b] for a,b in [(9,10),(11,12),(13,14),(15,16),(17,18)])
  assert all(0<=a<=255 for a in v[31:43])
 r.update(passed=True,probe_passed=v[0]==0x731,raw_result=v,control_registers=v[4:7],flags=v[1:4],GR04_before_after=v[9:11],requested=v[23:27],GR04_read=v[27:31],CR22_first=v[31:35],CR22_direct=v[35:39],CR22_reselected=v[39:43],distinct_first_read_values=len(set(v[31:35])) if v[22]==4 else None,cleanup_ok=bool(v[20]),selectors_restored=bool(v[19]),automatic_dashboard_return=True,normal_windows_shutdown=False,CR22_write_semantics_proved=False)
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
