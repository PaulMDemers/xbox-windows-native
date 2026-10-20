"""Review exported scene, trace and cleanup; never reopen this runtime."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn612/pc001/cold1-002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
import pefile
from Registry import Registry
from scene_compare import qualify
from analyze_trace001 import analyze
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
out=K/'review001.json';assert not out.exists();r=dict(passed=False,physical_access=False)
try:
 state=read('ntfs-phase1.json');cold=read('ntfs-cold1-002.json');build=read('build001.json');src=read('source001.json')
 assert state['closed'] and state['exit_code']==0 and cold['complete']
 assert not any(state.get(n) for n in ['host_quit','host_terminate','host_kill','deadline','space_stop'])
 assert cold['audit_unchanged'] and cold['source_unchanged'] and cold['normal_shutdown_delta']==1
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives'])
 manifest=json.loads((P/'manifest.json').read_text());logs=P/'files/xwn612';run=(logs/'runner.txt').read_text()
 for row in build['rows']:assert manifest['xwn612-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 text=(P/'files/xwn612-kit/copy-verified.txt').read_text();assert 'verified=1' in text and 'files=503' in text
 reg=Registry.Registry(str(P/'files/WINNT/system32/config/software'))
 try:reg.open('Fish Technology Group')
 except Registry.RegistryKeyNotFoundException:pass
 else:raise AssertionError('temporary game registry remained')
 assets=read('asset-integrity001.json');changed=[]
 for name,v in assets.items():
  actual=manifest['xwn612-kit/'+name.lower()]
  if actual['sha256']!=v['sha256']:changed.append(dict(name=name,before=v['sha256'],after=actual['sha256']))
 assert {v['name'] for v in changed}<={'game/Data/CSS0.DAT','game/Data/Game.cfg'}
 saved=P/'files/xwn612-kit/game/Saved Games/XWN593.SV4';assert sha(saved)==src['save']['sha256'] and saved.stat().st_size==src['save']['bytes']
 r.update(cleanup_passed=True,asset_changes=changed,normal_shutdown_delta=1,new_system_events=cold['new_system_events'])
 required=['display_preflight_passed=1','input_sequence_submitted=1','game_exit=0','registry_restored=1','restart_requested=1','load_file_bytes=290244','load_dialog_count=1','load_edit_count=1','load_path_readback=1','load_click_posted=1','load_dialog_gone=1','camera_right_submitted=1','park_phase_requested=1','park_phase_ack_wait=0','park_phase_acknowledged=1']
 for token in required:assert token in run,token
 assert run.count('load_click_posted=1')==1 and run.count('park_phase_requested=1')==1 and run.count('park_reference_match=1')==2
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
 game=Path('C:/xwn566/transfer002/game/RCT.EXE');assert sha(game)==assets['game/RCT.EXE']['sha256']
 pe=pefile.PE(str(game))
 trace=analyze((logs/'trace.txt').read_text(),pe.OPTIONAL_HEADER.ImageBase,pe.OPTIONAL_HEADER.SizeOfImage);(K/'trace-review001.json').write_text(json.dumps(trace,indent=2)+'\n')
 r.update(passed=True,trace_pairs=trace['total_pairs'],rct_stretch_per_phase=trace['rct_stretch_per_phase'],formats=trace['formats'])
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('606 independent saved scene, phase trace and cold cleanup passed; visual inspection pending')
