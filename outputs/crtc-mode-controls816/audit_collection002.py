"""Audit retained816 files locally after one collection; never recollect."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn816')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit002.json';assert not out.exists()
r={'passed':False,'physical_access':False,'auditor_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 rows=sorted(c['reports'].items())
 assert [v['data']['phase'] for _,v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','crtc_mode_controls_armed','crtc_mode_controls_returned','restart_requested']
 for name,v in rows:
  p=P/'collection001'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'] and read(p)==v['data']
 for name,h in read(K/'sources001.json').items():assert sha(K/name)==h
 for name,h in read(K/'review001.json')['checks'].items():assert sha(K/name)==h
 build=read(K/'build002.json');assert build['passed']
 for name,v in build['files'].items():assert sha(P/'build002'/name)==v['sha256']
 stage=read(K/'stage001.json');assert stage['completed'] and stage['controller_sha256']==sha(K/'physical.py')
 assert stage['staged']['/E/Applications/XWNMode816/default.xbe']['sha256']==sha(P/'build002/bin/default.xbe')
 assert all(v['data']['kernel_qpc_frequency']==3375000 and v['data']['kernel_qpc_frequency_high']==0 for _,v in rows[1:])
 d=rows[-1][1]['data'];v=d['kernel_sample_words'];assert len(v)==917 and rows[-2][1]['data']['kernel_sample_words']==v
 assert d['tool']=='xwn-native-mode816' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert f['physical']%4096==0 and 0<=f['physical']<0x4000000 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 from audit_logic import validate
 validated=validate(v)
 observation=read(K/'observation002.json')
 expected='green' if v[0]==0x816 else 'orange' if v[0] in [0x8168,0x8165,0x8169,0x816b,0x816d,0x816e,0x81610,0x81612,0x81614,0x81616,0x81618,0x8161a,0x8161c,0x8161e,0x81620,0x81622,0x81624,0x81626,0x81628,0x8162a,0x8162c,0x8162e,0x81630,0x81632,0x81634,0x81636,0x81638,0x8163a,0x8163c,0x8163e,0x81640,0x81642,0x81644,0x81646,0x81648] else 'red'
 assert observation['mode']=='unattended_authorized' and not observation['manual_reset_reported']
 assert observation['visual_result']=='not_observed'
 dashboard=read(K/'dashboard002.json');launch=read(K/'launch001.json')
 assert dashboard['authenticated'] and dashboard['reachable'] and launch['utc']<dashboard['utc']<=c['utc']
 assert d['complete'] and all(not row['data']['complete'] for _,row in rows[:-1])
 r.update(passed=True,raw_result=v,result=validated,automatic_dashboard_return_inferred=True,visual_result_observed=False,expected_top_bar=expected,normal_windows_shutdown=False,full_mode_replay=False,four_remaining_controls_kernel_only=True,CR1b_CR22_CR33_written=False)

except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
