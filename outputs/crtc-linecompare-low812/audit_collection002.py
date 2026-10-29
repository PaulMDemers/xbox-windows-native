"""Audit retained812 files locally after one collection; never recollect."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn812')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit002.json';assert not out.exists()
r={'passed':False,'physical_access':False,'auditor_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 rows=sorted(c['reports'].items())
 assert [v['data']['phase'] for _,v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','crtc_linecompare_low_control_armed','crtc_linecompare_low_control_returned','restart_requested']
 for name,v in rows:
  p=P/'collection001'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'] and read(p)==v['data']
 for name,h in read(K/'sources001.json').items():assert sha(K/name)==h
 for name,h in read(K/'review003.json')['checks'].items():assert sha(K/name)==h
 build=read(K/'build002.json');assert build['passed']
 for name,v in build['files'].items():assert sha(P/'build002'/name)==v['sha256']
 stage=read(K/'stage001.json');assert stage['completed'] and stage['controller_sha256']==sha(K/'physical.py')
 assert stage['staged']['/E/Applications/XWNMode812/default.xbe']['sha256']==sha(P/'build002/bin/default.xbe')
 assert all(v['data']['kernel_qpc_frequency']==3375000 and v['data']['kernel_qpc_frequency_high']==0 for _,v in rows[1:])
 d=rows[-1][1]['data'];v=d['kernel_sample_words'];assert len(v)==820 and rows[-2][1]['data']['kernel_sample_words']==v
 assert d['tool']=='xwn-native-mode812' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert f['physical']%4096==0 and 0<=f['physical']<0x4000000 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 from audit_logic import validate
 validated=validate(v)
 observation=read(K/'observation001.json')
 expected='green' if v[0]==0x812 else 'orange' if v[0] in [0x8128,0x8125,0x8129,0x812b,0x812d,0x812e,0x81210,0x81212,0x81214,0x81216,0x81218,0x8121a,0x8121c,0x8121e,0x81220,0x81222,0x81224,0x81226,0x81228,0x8122a,0x8122c,0x8122e,0x81230,0x81232,0x81234,0x81236,0x81238,0x8123a,0x8123c,0x8123e,0x81240,0x81242,0x81244,0x81246,0x81248] else 'red'
 assert observation['mode']=='unattended_authorized' and not observation['manual_reset_reported']
 assert observation['visual_result']=='not_observed'
 dashboard=read(K/'dashboard002.json');launch=read(K/'launch001.json')
 assert dashboard['authenticated'] and dashboard['reachable'] and launch['utc']<dashboard['utc']<=c['utc']
 assert d['complete'] and all(not row['data']['complete'] for _,row in rows[:-1])
 r.update(passed=True,raw_result=v,result=validated,automatic_dashboard_return_inferred=True,visual_result_observed=False,expected_top_bar=expected,normal_windows_shutdown=False,full_mode_replay=False,horizontal_prefix_seven_vertical_words_diagnostic=True,CR1b_CR22_CR33_written=False)

except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
