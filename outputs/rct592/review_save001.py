"""Gate phase2 on exact physical save readback, normal restart and cleanup."""
import hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=K/'save-phase1-review001.json';assert not out.exists()
st=read('stage001.json');col=read('collection001.json');a=read('audit1.json');reg=read('registry-review001.json');u=read('user-hive-audit001.json');w=read('welcome-review001.json')
assert st['completed'] and col['completed'] and col['hook_removed']
runner=col['files'].get('/E/xwn586/runner.txt');fields={}
if runner:
 assert sha(runner['path'])==runner['sha256']
 text=Path(runner['path']).read_text()
 for line in text.splitlines():
  if '=' in line and not line.startswith(('window ','module=')):
   key,value=line.split('=',1);fields.setdefault(key,[]).append(value)
save=next((r for n,r in col['files'].items() if n.lower()=='/e/xwn586-kit/game/saved games/xwn586.sv4'),None)
new=not any(n.lower().endswith('/saved games/xwn586.sv4') for n in st['staged'])
exact=bool(save and 32<save['bytes']<8*1024**2 and Path(save['path']).stat().st_size==save['bytes'] and sha(save['path'])==save['sha256'])
checks=dict(runner_present=bool(runner),new_save=new and exact,save_target_absent=fields.get('save_target_absent')==['1'],one_save_submission=fields.get('save_click_posted')==['1'],dialog_closed=fields.get('save_dialog_gone')==['1'],save_observed=fields.get('save_phase_file_observed')==['1'],saved_size_matches=bool(save and fields.get('saved_file_bytes')==[str(save['bytes'])]),sequence_submitted=fields.get('input_sequence_submitted')==['1'],normal_shutdown=a['events']['system']['normal_shutdown_delta']==1,game_exit_zero=fields.get('game_exit')==['0'],no_forced_termination='forced_terminate' not in fields,desktop_preserved=fields.get('desktop_restored')==['1'],registry_restored=reg['passed'] and fields.get('registry_restored')==['1'],restart_requested=fields.get('restart_requested')==['1'],hives_clean=a['hives_clean'] and u['passed'],welcome_preserved=w['passed'],hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'])
r=dict(passed=all(checks.values()),checks=checks,save=save,runner_fields=fields,phase1_closed=True,overall_experiment='OPEN; phase2 not admitted unless this review and visual save-stage review pass',physical_access=True,console_writes=False,limits='New saved-file and normal-restart evidence; only a later successful Load can qualify observed game-state restoration. No general FATX health/FPS/GPU claim.')
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(checks))
