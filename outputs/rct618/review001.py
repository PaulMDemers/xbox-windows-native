"""Review exported scene, trace and cleanup; never reopen this runtime."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn618/pc001/cold1-002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
import pefile
from Registry import Registry
from scene_compare import qualify
from cost_oracle import analyze
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False)
try:
 state=read('ntfs-phase1.json');cold=read('ntfs-cold1-002.json');build=read('build001.json');src=read('source001.json')
 assert state['closed'] and state['exit_code']==0 and cold['complete']
 assert not any(state.get(n) for n in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
 assert cold['audit_unchanged'] and cold['source_unchanged'] and cold['normal_shutdown_delta']==1
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives'])
 manifest=json.loads((P/'manifest.json').read_text());logs=P/'files/xwn618';run=(logs/'runner.txt').read_text()
 for row in build['rows']:assert manifest['xwn618-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 text=(P/'files/xwn618-kit/copy-verified.txt').read_text();assert 'verified=1' in text and 'files=503' in text
 reg=Registry.Registry(str(P/'files/WINNT/system32/config/software'))
 try:reg.open('Fish Technology Group')
 except Registry.RegistryKeyNotFoundException:pass
 else:raise AssertionError('temporary game registry remained')
 assets=read('asset-integrity001.json');changed=[]
 for name,v in assets.items():
  actual=manifest['xwn618-kit/'+name.lower()]
  if actual['sha256']!=v['sha256']:changed.append(dict(name=name,before=v['sha256'],after=actual['sha256']))
 assert {v['name'] for v in changed}<={'game/Data/CSS0.DAT','game/Data/Game.cfg'}
 saved=P/'files/xwn618-kit/game/Saved Games/XWN593.SV4';assert sha(saved)==src['save']['sha256'] and saved.stat().st_size==src['save']['bytes']
 r.update(cleanup_passed=True,asset_changes=changed,normal_shutdown_delta=1,new_system_events=cold['new_system_events'])
 required=['display_preflight_passed=1','input_sequence_submitted=1','game_exit=0','registry_restored=1','restart_requested=1','load_file_bytes=290244','load_dialog_count=1','load_edit_count=1','load_path_readback=1','load_click_posted=1','load_dialog_gone=1','camera_right_submitted=1']
 for token in required:assert token in run,token
 assert run.count('load_click_posted=1')==1 and run.count('park_reference_match=1')==2
 assert 'forced_terminate=' not in run
 ref=Path(src['reference']['path']);assert sha(ref)==src['reference']['sha256']
 names=['title','scenarios','objective','window-options','park-before-move','camera-moved','load-menu','park-loaded','park-loaded-stable'];images={};captures=[]
 for i,name in enumerate(names):
  p=logs/('%02d-%s.bmp'%(i,name));data=p.read_bytes()
  assert len(data)==1228854 and data[:2]==b'BM' and struct.unpack_from('<I',data,10)[0]==54
  assert struct.unpack_from('<IiiHHII',data,14)==(40,640,-480,1,32,0,1228800)
  assert 'capture=%s index=%d success=1'%(name,i) in run
  images[name]=Image.open(p).convert('RGB');captures.append(dict(name=p.name,path=str(p),sha256=sha(p)))
 scene=qualify(Image.open(ref).convert('RGB'),images['park-before-move'],images['camera-moved'],images['park-loaded'],images['park-loaded-stable'])
 (K/'scene-review001.json').write_text(json.dumps(scene,indent=2)+'\n')
 r.update(scene=scene,captures=captures);assert scene['passed'],'saved scene comparison failed'
 cost=(logs/'cost.txt').read_text()
 host=json.loads(Path('C:/xwn618/pc001/phase1/serial-host.json').read_text())
 trace=(logs/'trace.txt').read_text()
 pe=pefile.PE('C:/xwn566/transfer002/game/RCT.EXE')
 result=analyze(cost,host,trace,pe.OPTIONAL_HEADER.ImageBase,pe.OPTIONAL_HEADER.SizeOfImage)
 ident=(logs/'identity.bin').read_bytes();assert len(ident)==16
 actual=result['cases']['1']['identity'];assert list(struct.unpack('<4I',ident))==actual[:2]+actual[3:]
 (K/'serial-host001.json').write_text(json.dumps(host,indent=2)+'\n')
 (K/'raw-counter-logs001.json').write_text(json.dumps(dict(cost=cost,runner=run,trace=trace),indent=2)+'\n')
 (K/'cost-review001.json').write_text(json.dumps(result,indent=2)+'\n')
 states=[]
 import re
 for tag in ['cost-before','cost-after']:
  match=re.search(r'input_state='+tag+r' tick=(\d+) valid=1 pid=(\d+) foreground=1 foreground_pid=(\d+) foreground_class=RollerCoaster Tycoon rect_read=1 origin_read=1 cursor_read=1 client=(\d+),(\d+),640,480 cursor=(\d+),(\d+) display=1024,768',run)
  assert match,tag
  values=list(map(int,match.groups()));assert values[1]==values[2]
  assert values[5]==values[3]+5 and values[6]==values[4]+5
  states.append(values)
 assert states[0][1:]==states[1][1:] and states[0][0]<=host['rows'][2]['tick']<=host['rows'][3]['tick']<=states[1][0]
 r.update(passed=True,cost=result,window_states=states)
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('618 saved scene, separate process costs, timed recorder activity and cold cleanup passed; visual inspection pending')
