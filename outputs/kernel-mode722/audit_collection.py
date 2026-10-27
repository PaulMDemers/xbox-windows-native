"""Local-only audit of the single722 collection. Does not reconnect/recollect."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn722')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'script_sha256':sha(Path(__file__))}
try:
 c=read(K/'collection001.json');s=read(K/'stage001.json');b=read(K/'build001.json')
 assert c['completed'] and c['dashboard_returned'] and c['unrelated_directory_entries_unchanged']
 assert s['completed'] and b['passed']
 for name,value in read(K/'sources001.json').items():assert sha(K/name)==value
 for name,value in read(K/'review001.json')['checks'].items():assert sha(K/name)==value
 for name,value in b['files'].items():assert sha(P/'build001'/name)==value['sha256']
 data=[]
 for name,v in sorted(c['reports'].items()):
  p=P/'collection001'/name;assert sha(p)==v['sha256'] and read(p)==v['data'];data.append(v['data'])
 r['report_count']=len(data)
 expected=['start']+['mode_requested','mode_captured','visible_captured']*3+['restart_requested']
 assert [v['phase'] for v in data]==expected
 assert [v['complete'] for v in data]==[False]*10+[True]
 assert data[0]['eligible'] and data[0]['pages']==16384 and data[0]['memory_status']==0
 settings=data[0]['settings'];assert settings&0xff==4 and settings&0x20000 and settings&0x80000
 assert all(v['settings']==settings and v['tool']=='xwn-kernel-mode722' and v['schema']==1 and
  v['gpu_revision']==0xd3 and v['mcp_revision']==0xd5 and not v['native_handoff'] and
  not v['diagnostic_gpu_data_writes'] and v['kernel']==data[0]['kernel'] for v in data)
 r['modes']=[];r['limits']=['Kernel-supported mode comparison, not native mode implementation proof.','Capture is sequential; moving hardware values are not an atomic snapshot.','Dashboard return is firmware restart, not Windows normal shutdown.','Directory entries and selected files checked, not a full FATX or hive audit.']
 for i,(width,height,color) in enumerate([(1280,720,0x2080ff),(720,480,0x00ff00),(1280,720,0x00ffff)]):
  req,now,held=data[1+i*3:4+i*3]
  assert req['stage']==now['stage']==held['stage']==i
  want=[width,height,32,60];assert req['requested']==now['requested']==now['sdk_mode']==want and now['applied']
  fb=now['framebuffer'];size=width*height*4
  assert fb['admitted'] and fb['bytes']==size and fb['pitch']==width*4
  assert 0<=fb['address']<0x4000000 and fb['address']%4096==0
  assert size<=fb['allocation']<=0x4000000-fb['address']
  assert fb['page_checks']==(size+4095)//4096 and fb['first_bad']==0xffffffff
  assert held['capture_ok'] and held['hold_ms']==12000 and held['pattern_color']==color
  for v in (now,held):
   assert v['selectors_restored'] and v['selectors']==v['selectors_after']
   assert v['flags'][0]==v['flags'][2] and not v['flags'][1]&0x200
   assert len(v['mmio'])==30 and len(v['crtc'])==31 and len(v['sequencer'])==5 and len(v['graphics'])==9
   assert len(dict(v['mmio']))==30 and len(dict(v['crtc']))==31
   mm=dict(v['mmio']);cr=dict(v['crtc'])
   assert mm[0x600800]==fb['address'] and mm[0x680818]+1==height and mm[0x680838]+1==width
   pitch=(cr[0x13]|((cr[0x19]&0xe0)<<3)|((cr[0x25]&0x20)<<6))<<3
   assert pitch==width*4 and cr[0x28]&15==3 and cr[0x39]==255
  m0,m1=dict(now['mmio']),dict(held['mmio']);c0,c1=dict(now['crtc']),dict(held['crtc'])
  r['modes'].append({'stage':i,'mode':want,'CR1b':[c0[0x1b],c1[0x1b]],'CR22':[c0[0x22],c1[0x22]],'680880':[m0[0x680880],m1[0x680880]],'680630':[m0[0x680630],m1[0x680630]],'changed_mmio':{hex(a):[m0[a],m1[a]] for a in m0 if m0[a]!=m1[a]},'changed_crtc':{hex(a):[c0[a],c1[a]] for a in c0 if c0[a]!=c1[a]}})
 low=data[5];mm=dict(low['mmio']);cr=dict(low['crtc'])
 targets={0x680884:0,0x680888:0,0x68088c:0x10001000,0x680890:0x10000000,0x680894:0x10000000,0x680898:0x10000000,0x68089c:0x10000000,0x680880:0x21101100,0x680630:2,0x68084c:0x00801080,0x6808c4:0x40801080,0x680508:0x3c20d,0x68050c:0x100a0400,0x100200:0x3070003,0x600804:3}
 targets.update(dict(zip([0x680800,0x680804,0x680808,0x68080c,0x680810,0x680814,0x680818,0x680820,0x680824,0x680828,0x68082c,0x680830,0x680834,0x680838],[479,524,479,489,492,0,479,719,779,719,738,770,0,719])))
 crtargets={0x14:0,0x17:0xe3,0x19:0x30,0x1b:5,0x22:255,0x33:0x11}
 r['kernel720x480_vs704_final_targets']={'mmio':{hex(a):{'target':v,'kernel':mm[a],'equal':v==mm[a]} for a,v in targets.items()},'crtc':{hex(a):{'target':v,'kernel':cr[a],'equal':v==cr[a]} for a,v in crtargets.items()}}
 r['comparison_limit']='704 CR19 setup10 becomes30 after geometry; comparison uses final30. Differences do not prove cause or justify firmware-state replay.'
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'reports':r['report_count'],'modes':r['modes']}))
