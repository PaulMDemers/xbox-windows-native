"""Offline audit of707 collected bytes; never reconnects or reopens a runtime."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn707')
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((K/'collection001.json').read_text());out=K/'audit001.json';assert not out.exists()
a={'passed':False,'physical_native_transition':False,'collection_sha256':sha((K/'collection001.json').read_bytes())}
try:
 assert r['completed'] and r['unrelated_directory_entries_unchanged']
 rows=[v['data'] for v in r['reports'].values()];d=rows[-1]
 assert [v['phase'] for v in rows]==['start','before_kernel_mode','allocation_checked','kernel_context_captured','before_allocations','after_allocations','allocations_released','pattern_submitted','restart_requested']
 for n,v in r['reports'].items():
  data=(P/'collection001'/n).read_bytes();assert sha(data)==v['sha256'] and json.loads(data)==v['data']
 assert d['complete'] and d['preflight_passed'] and d['selectors_restored'] and d['allocation_refusal_bits']==0
 p=d['allocation_plan_words'];assert len(p)==31
 assert p[1:4]==[1048576,1048576,1] and p[5:9]==[32768,32768,1,0]
 assert p[9]==p[4] and p[10]<=p[9] and p[9]+32768<=p[10]+p[11]<=0x80000000
 assert all(not p[i]%4096 for i in [0,4,9,10,11,28]) and 32768<=p[11]<=131072
 spans=[(p[0],p[0]+p[2]),(p[4],p[4]+p[6]),(p[28],p[28]+p[30])]
 assert 0x200000<=spans[0][0]<spans[0][1]<=0x2000000
 assert 0x1000000<=spans[1][0]<spans[1][1]<=0x2000000
 assert 0x2000000<=spans[2][0]<spans[2][1]<=0x4000000 and p[29]==3686400 and p[30]>=p[29]
 ov=lambda x,y:max(x[0],y[0])<min(x[1],y[1])
 assert all(not ov(x,y) for i,x in enumerate(spans) for y in spans[i+1:])
 assert not ov(spans[2],(0x2600000,0x2800000)) and len(set(p[12:20]))==8
 for i in range(8):
  x=p[12+i];assert not x%4096 and p[20+i]==x+4095 and x+4096<=0x4000000
  assert not ov((x,x+4096),spans[0]) and not ov((x,x+4096),spans[2])
  assert not ov((x,x+4096),spans[1]) or x==p[4]+4096*i
 assert d['cleanup']=={'copies_verified':True,'bytes':32768,'alias_created':True,'alias_free_status':0,'source_freed':True,'stub_freed':True,'native_transition':False}
 observation=json.loads((K/'observation001.json').read_text());assert observation['top_bar']=='green' and observation['automatic_dashboard_return']
 old=json.loads((K.parent/'native-preflight706/collection001.json').read_text());previous=list(old['reports'].values())[-1]['data']
 keys=['pci_kernel_reads','crtc_kernel_reads','sequencer_kernel_reads']
 a['kernel_context_equal_to706']={n:d[n]==previous[n] for n in keys}
 a['context_differences']={n:{'706':previous[n],'707':d[n]} for n in keys if d[n]!=previous[n]}
 a.update(passed=True,source=hex(p[0]),stub=hex(p[4]),framebuffer=hex(p[28]),alias_pages=[hex(v) for v in p[12:20]],user_green_and_returned=True)
except BaseException as e:a['failure']=repr(e);raise
finally:
 a['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(a,indent=2)+'\n')
print(json.dumps(a,indent=2))
