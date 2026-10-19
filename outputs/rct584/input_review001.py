"""MIT. Native sequence contract, separate from independently observed gameplay."""
import hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn584/pc001/collection001');out=K/'input-review001.json'
assert not out.exists()
runner=(P/'runner.txt').read_text();cleanup=json.loads((K/'review001.json').read_text());captures=json.loads((K/'capture-review001.json').read_text())
expected=['title','scenarios','objective','window-options','window-before','window-edge','window-arrow','window-drag','mode-menu','full-before','full-edge','full-arrow','full-drag','restored-options','restored-window']
actual=re.findall(r'^capture=(\S+) index=(\d+) success=(\d+) error=(\d+)$',runner,re.M)
checks=dict(cleanup=cleanup['passed'],sequence_submission=cleanup['runner_fields'].get('input_sequence_submitted')==['1'],title_ready=cleanup['runner_fields'].get('title_ready')==['1'],exact_capture_order=[r[0] for r in actual]==expected,capture_indices=[int(r[1]) for r in actual]==list(range(15)),capture_calls_succeeded=bool(actual) and all(r[2]=='1' for r in actual),image_structure=captures['structurally_valid'],complete_matrix=captures['complete_case_matrix'],nonuniform_images=captures['all_images_nonuniform'])
out.write_text(json.dumps(dict(passed=all(checks.values()),checks=checks,physical_access=False,runner_sha256=hashlib.sha256((P/'runner.txt').read_bytes()).hexdigest(),limits='Harness contract only. Inspect screenshots independently for the actual UI stages and landscape movement; sent input and changed pixels are not game behavior proof.'),indent=2)+'\n')
print(json.dumps(checks))
