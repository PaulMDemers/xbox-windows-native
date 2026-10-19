"""MIT. Exercise the actual dashboard-retry admission without console access."""
import copy, hashlib, importlib.util, json
from pathlib import Path
K = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location('admission558', K / 'controller.py')
c = importlib.util.module_from_spec(s); s.loader.exec_module(c)
original_read = c.read
c.boot_work_closed()  # Actual prerequisite records, no FTP.
paths = [K / 'ready001.json', K.parent / 'perspective557/final001.json',
         K.parent / 'perspective556/final-review.json',
         K.parent / 'boot-primer543/final001.json',
         K.parent / 'warm-pre-pci544/final001.json']
records = {str(p): original_read(p) for p in paths if p.exists()}
rows = []
cases = [(0, 'user_requested_retry', False), (0, 'at_dashboard', False),
         (0, 'full_power_cycle_confirmed', True), (1, 'closed', False),
         (1, 'temporary_hook_removed', False),
         (2, 'scoped_perspective_passed', False), (3, 'closed', False)]
for index, key, value in cases:
    modeled = copy.deepcopy(records); modeled[str(paths[index])][key] = value
    c.read = lambda p: modeled[str(p)] if str(p) in modeled else original_read(p)
    try:
        c.boot_work_closed()
    except AssertionError:
        rows.append(dict(key=key, value=value, refused=True))
    else:
        raise AssertionError(key)
c.read = original_read
c.boot_work_closed()
out = K / 'admission-host001.json'; assert not out.exists()
out.write_text(json.dumps(dict(passed=True, actual_admission_passed=True,
    negative_cases=rows, physical_access=False,
    controller_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest()),
    indent=2)+'\n', encoding='utf-8')
print('PASS actual dashboard admission and seven refusals')
