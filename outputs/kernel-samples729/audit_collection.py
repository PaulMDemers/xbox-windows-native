"""Read retained729 collection locally. No connection or recollection."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn729')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'auditor_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 rows=sorted(c['reports'].items())
 assert [v['data']['phase'] for _,v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','write_control_armed','write_control_returned','restart_requested']
 for name,v in rows:
  p=P/'collection001'/name;assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'] and read(p)==v['data']
 for name,h in read(K/'sources001.json').items():assert sha(K/name)==h
 for name,h in read(K/'review001.json')['checks'].items():assert sha(K/name)==h
 build=read(K/'build001.json');assert build['passed']
 for name,v in build['files'].items():assert sha(P/'build001'/name)==v['sha256']
 stage=read(K/'stage001.json');assert stage['completed']
 assert stage['controller_sha256']==sha(K/'physical.py')
 assert stage['staged']['/E/Applications/XWNMode729/default.xbe']['sha256']==sha(P/'build001/bin/default.xbe')
 d=rows[-1][1]['data'];v=d['kernel_sample_words'];assert len(v)==125
 assert rows[-2][1]['data']['kernel_sample_words']==v
 assert d['tool']=='xwn-native-mode729' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert 0<=f['physical']<0x4000000 and f['physical']%4096==0 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 assert v[2]==v[4] and not v[3]&0x200 and v[5]&0x80000001==0x80000001 and not v[7]&0x20
 assert v[0] in [0x729,0x7291,0x7292,0x7293,0x7295,0x7296,0x7298,0x7299]
 assert v[1]<=2 and v[43]<=1 and v[44]<=1
 assert v[53]==v[1]|(v[43]<<8)|(v[44]<<16)
 assert v[42]==v[18]|(v[19]<<1)|((v[38]==32 and not v[39])<<2)|(v[38]<<8)|(v[1]<<16)|(v[43]<<24)
 expected_color='green' if v[0]==0x729 else 'orange' if v[0] in (0x7295,0x7298) else 'red'
 observation=read(K/'observation001.json');assert observation['top_bar']==expected_color
 assert observation['automatic_return_observed'] and not observation['manual_reset']
 assert d['complete'] and all(not row['data']['complete'] for _,row in rows[:-1])
 if v[1]==2:
  assert v[118]==32
  seq=[v[29]]+v[86:118]
  assert v[119:122]==[sum(a!=b for a,b in zip(seq,seq[1:])),min(seq),max(seq)]
 else:assert v[54:118]==[0xffffffff]*64 and v[118:122]==[0]*4
 if v[0]==0x729:assert v[18:20]==[1,1] and v[50:52]==[5,5] and v[26]==v[31]==0x85
 previous=read(K.parent/'kernel-interaction728/audit001.json')['raw_result']
 r.update(passed=True,report_count=7,probe_passed=v[0]==0x729,code=hex(v[0]),raw_result=v,flags=v[2:5],control_registers=v[5:8],selectors_restored=bool(v[19]),full_baseline_cleanup_passed=bool(v[18]),mmio630=v[20:26],cr1b=v[26:32],prewrite=v[47:50],direct_indexed=v[50:52],late_count=v[38],late_changes=v[39],blank630=v[54:86],blank1b=v[86:118],blank_count_changes_min_max=v[118:122],aftergate_beforeSEQ=v[122:125],previous728_cr1b=previous[26:32],automatic_dashboard_return=True,normal_windows_shutdown=False,native_handoff=False)

except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
