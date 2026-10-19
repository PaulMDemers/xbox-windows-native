"""Physical runner/shutdown contract, distinct from independent image review."""
import hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
out=K/'review002.json';assert not out.exists()
col=read('collection001.json');assert col['completed']
row=col['files']['/E/xwn575/runner.txt'];data=Path(row['path']).read_bytes()
assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
runner=data.decode('ascii').replace('\r\n','\n');fields={}
for line in runner.splitlines():
 if '=' in line and not line.startswith(('window ','module=')):
  key,value=line.split('=',1);fields.setdefault(key,[]).append(value)
audit=read('audit1.json');reg=read('registry-review001.json');captures=read('capture-review002.json')
expected=['title','scenarios','objective','window-options','window-before','window-edge','window-arrow','window-drag','mode-menu','full-before','full-edge','full-arrow','full-drag','restored-options','restored-window']
actual=re.findall(r'^capture=(\S+) index=(\d+) success=(\d+) error=(\d+)$',runner,re.M)
cleanup=dict(desktop_restored=fields.get('desktop_restored')==['1'],restart_requested=fields.get('restart_requested')==['1'],restart_privilege=fields.get('restart_privilege')==['1'],registry_restored=reg['passed'],runner_restored=fields.get('registry_restored')==['1'],normal_shutdown=audit['events']['system']['normal_shutdown_delta']==1,game_exit_zero=fields.get('game_exit')==['0'],no_forced_termination='forced_terminate' not in fields,hives_clean=audit['hives_clean'],hook_removed=col['hook_removed'],protected_code_exact=col['protected_code_exact'])
contract=dict(sequence_submission=fields.get('input_sequence_submitted')==['1'],title_ready=fields.get('title_ready')==['1'],exact_capture_order=[r[0] for r in actual]==expected,capture_indices=[int(r[1]) for r in actual]==list(range(15)),capture_calls_succeeded=bool(actual) and all(r[2]=='1' for r in actual),image_structure=captures['structurally_valid'],complete_matrix=captures['complete_case_matrix'],nonuniform_images=captures['all_images_nonuniform'])
r=dict(cleanup_qualified=all(cleanup.values()),submission_contract_passed=all(contract.values()),cleanup_checks=cleanup,submission_checks=contract,runner_fields=fields,capture_rows=actual,physical_access=True,console_writes=False,runner_sha256=row['sha256'],limits='Runner and cold hive/event contract only. Submitted input and valid images do not prove camera behavior. No physical-display observation, frame-rate or acceleration proof.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(cleanup=cleanup,submission=contract)))
