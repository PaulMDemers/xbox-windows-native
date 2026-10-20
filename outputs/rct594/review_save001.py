"""Gate phase2 on exact physical save readback, normal restart and cleanup."""
import hashlib,json,re,struct
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=K/'save-phase1-review001.json';assert not out.exists()
st=read('stage002.json');col=read('collection001.json');a=read('audit1.json');reg=read('registry-review001.json');u=read('user-hive-audit001.json');w=read('welcome-review001.json')
assert st['completed'] and col['completed'] and col['hook_removed']
runner=col['files'].get('/E/xwn593/runner.txt');fields={}
if runner:
 assert sha(runner['path'])==runner['sha256']
 text=Path(runner['path']).read_text()
 for line in text.splitlines():
  if '=' in line and not line.startswith(('window ','module=')):
   key,value=line.split('=',1);fields.setdefault(key,[]).append(value)
save=next((r for n,r in col['files'].items() if n.lower()=='/e/xwn593-kit/game/saved games/xwn593.sv4'),None)
new=not any(n.lower().endswith('/saved games/xwn593.sv4') for n in st['staged'])
exact=bool(save and 32<save['bytes']<8*1024**2 and Path(save['path']).stat().st_size==save['bytes'] and sha(save['path'])==save['sha256'])
checks=dict(runner_present=bool(runner),new_save=new and exact,save_target_absent=fields.get('save_target_absent')==['1'],one_save_submission=fields.get('save_click_posted')==['1'],dialog_closed=fields.get('save_dialog_gone')==['1'],save_observed=fields.get('save_phase_file_observed')==['1'],saved_size_matches=bool(save and fields.get('saved_file_bytes')==[str(save['bytes'])]),sequence_submitted=fields.get('input_sequence_submitted')==['1'],normal_shutdown=a['events']['system']['normal_shutdown_delta']==1,game_exit_zero=fields.get('game_exit')==['0'],no_forced_termination='forced_terminate' not in fields,desktop_preserved=fields.get('desktop_restored')==['1'],registry_restored=reg['passed'] and fields.get('registry_restored')==['1'],restart_requested=fields.get('restart_requested')==['1'],hives_clean=a['hives_clean'] and u['passed'],welcome_preserved=w['passed'],hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'])
observed=fields.get('saved_sha1_byte',[])
observed_hash=bytes(int(v) for v in observed).hex() if len(observed)==20 else None
data=Path(save['path']).read_bytes() if save else b''
value=lambda k:int(fields.get(k,['-1'])[0])
prior='/E/xwn593-kit/game/Saved Games/XWN586.SV4'
oldsave=col['files'].get(prior)
captures=[r for n,r in col['files'].items() if n.startswith('/E/xwn593/') and n.endswith('-park-after-save.bmp')]
valid=[]
for row in captures:
 b=Path(row['path']).read_bytes()
 valid.append(sha(row['path'])==row['sha256'] and len(b)==54+640*480*4 and b[:2]==b'BM' and struct.unpack_from('<I',b,2)[0]==len(b) and struct.unpack_from('<I',b,10)[0]==54 and struct.unpack_from('<IiiHHII',b,14)==(40,640,-480,1,32,0,640*480*4))
checks.update(guest_sha1_matches_cold=bool(data) and observed_hash==hashlib.sha1(data).hexdigest(),stable_readback=value('saved_equal_reads')>=3 and value('saved_stable_ms')>=1000,within_deadline=0<=value('saved_wait_elapsed_ms')<30000,no_wait_failure=not any(k in fields for k in ['saved_wait_fatal','saved_wait_timeout']),post_save_image=len(valid)==1 and all(valid),prior_save_preserved=bool(oldsave) and oldsave['sha256']==st['staged'][prior]['sha256']=='87f2ddaf852a1ebfc9f8b2c734bbdedfffe83ce8e2a97fb33d0bb41ce7909fd2' and sha(oldsave['path'])==oldsave['sha256'])
r=dict(passed=all(checks.values()),checks=checks,save=save,guest_sha1=observed_hash,cold_sha1=hashlib.sha1(data).hexdigest() if data else None,runner_fields=fields,phase1_closed=True,overall_experiment='Save phase only; Load remains untested',physical_access=True,console_writes=False,limits='New saved-file and normal-restart evidence; only a later successful Load can qualify observed game-state restoration. No general FATX health/FPS/GPU claim.')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(checks))
