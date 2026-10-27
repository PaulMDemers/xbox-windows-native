"""Read retained723 collection locally. No connection or recollection."""
from pathlib import Path
import hashlib,json,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn723')
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
 assert stage['staged']['/E/Applications/XWNMode723/default.xbe']['sha256']==sha(P/'build001/bin/default.xbe')
 d=rows[-1][1]['data'];v=d['kernel_setup_prefix_words'];assert len(v)==66
 assert rows[-2][1]['data']['kernel_setup_prefix_words']==v
 assert d['tool']=='xwn-native-mode723' and d['kernel']==[1,0,5838,1] and d['gpu_revision']==0xd3 and d['mcp_revision']==0xd5
 assert not d['native_transition'] and not d['native_handoff_performed'] and d['selectors_restored']
 assert d['sdk_mode']==[1280,720,32,60] and d['geometry']['pitch_bytes']==5120
 f=d['framebuffer'];assert f['admitted'] and f['contiguous'] and f['page_checks']==900 and f['bytes']==3686400 and f['first_bad_offset']==0xffffffff and f['physical']==f['scanout']
 assert 0<=f['physical']<0x4000000 and f['physical']%4096==0 and f['allocation']>=f['bytes'] and f['bytes']<=0x4000000-f['physical']
 assert v[4]==v[6] and not v[5]&0x200 and v[7]&0x80000001==0x80000001 and not v[9]&0x20
 assert v[0] in [0x723,0x7231,0x7232,0x7233,0x7234,0x7235,0x7236,0x7238]
 expected=[0,0,0x10001000,0x10000000,0x10000000,0x10000000,0x10000000,0x21101100,2,0x00801080,0x40801080]
 before=expected.copy();before[8]=3
 if v[0]==0x723:
  assert v[:4]==[0x723,11,4,0xffffffff]
  assert v[12:18]==[1,1,9,9,0xfe,0xfe] and v[19:21]==[1,1]
  assert v[21:32]==before and v[32:43]==expected and v[43:54]==before
  assert v[54:58]==[0,0xe3,0x51,0x85] and v[58:62]==[0,0xe3,0x10,5] and v[62:66]==[0,0xe3,0x51,5]
 expected_color='green' if v[0]==0x723 else 'orange' if v[0]==0x7238 else 'red'
 observation=read(K/'observation001.json');assert observation['top_bar']==expected_color and observation['automatic_return_observed'] and not observation['manual_reset']
 assert d['complete'] and all(not row['data']['complete'] for _,row in rows[:-1])
 r.update(passed=True,report_count=7,prefix_passed=v[0]==0x723,code=hex(v[0]),attempted_mmio=v[1],attempted_crtc=v[2],first_mismatch=v[3],flags=v[4:7],control_registers=v[7:10],selectors_restored=bool(v[19]),cleanup_passed=bool(v[20]),mmio_before=v[21:32],mmio_written_readback=v[32:43],mmio_cleanup=v[43:54],crtc_before=v[54:58],crtc_written_readback=v[58:62],crtc_cleanup=v[62:66],CR22_before_after=v[16:18],retained_CR1b=v[65],full_register_restoration=False,automatic_dashboard_return=True,normal_windows_shutdown=False,native_handoff=False)
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
