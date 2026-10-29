"""Audit retained796 files locally after one collection; never recollect."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn796')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'auditor_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 rows=sorted(c['reports'].items())
 assert [v['data']['phase'] for _,v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','crtc_vdisplay_high_control_armed','crtc_vdisplay_high_control_returned','restart_requested']
 for name,v in rows:
  p=P/'collection001'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'] and read(p)==v['data']
 for name,h in read(K/'sources001.json').items():assert sha(K/name)==h
 for name,h in read(K/'review001.json')['checks'].items():assert sha(K/name)==h
 build=read(K/'build001.json');assert build['passed']
 for name,v in build['files'].items():assert sha(P/'build001'/name)==v['sha256']
 stage=read(K/'stage001.json');assert stage['completed'] and stage['controller_sha256']==sha(K/'physical.py')
 assert stage['staged']['/E/Applications/XWNMode796/default.xbe']['sha256']==sha(P/'build001/bin/default.xbe')
 assert all(v['data']['kernel_qpc_frequency']==3375000 and v['data']['kernel_qpc_frequency_high']==0 for _,v in rows[1:])
 d=rows[-1][1]['data'];v=d['kernel_sample_words'];assert len(v)==610 and rows[-2][1]['data']['kernel_sample_words']==v
 assert d['tool']=='xwn-native-mode796' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert f['physical']%4096==0 and 0<=f['physical']<0x4000000 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 from audit_logic import validate
 validated=validate(v)
 observation=read(K/'observation001.json')
 expected='green' if v[0]==0x796 else 'orange' if v[0] in [0x7968,0x7965,0x7969,0x796b,0x796d,0x796e,0x79610,0x79612,0x79614,0x79616,0x79618,0x7961a,0x7961c,0x7961e,0x79620,0x79622,0x79624,0x79626,0x79628,0x7962a,0x7962c,0x7962e,0x79630,0x79632,0x79634,0x79636,0x79638,0x7963a] else 'red'
 assert observation['mode']=='unattended_authorized' and not observation['manual_reset_reported']
 assert observation['visual_result']=='not_observed' and read(K/'dashboard001.json')['reachable']
 assert d['complete'] and all(not row['data']['complete'] for _,row in rows[:-1])
 r.update(passed=True,raw_result=v,result=validated,automatic_dashboard_return_inferred=True,visual_result_observed=False,expected_top_bar=expected,normal_windows_shutdown=False,full_mode_replay=False,horizontal_prefix_seven_vertical_words_diagnostic=True,CR1b_CR22_CR33_written=False)

except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
