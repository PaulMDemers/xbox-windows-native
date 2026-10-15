"""Type only the already-installed witness path into the observed Run dialog."""
import importlib.util, json, time
from pathlib import Path
K = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pc', K / 'pc-run001.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = K / 'manual-witness004.json'
assert not out.exists()
keys = ['c', 'shift-semicolon', 'backslash', 'x', 'w', 'n', '4', '0', '4', 'dot', 'e', 'x', 'e']
with m.Qmp(m.P / 'phase04/qmp.sock') as q:
    for key in keys:
        q.call('human-monitor-command', {'command-line': 'sendkey ' + key})
        time.sleep(0.15)
    shot = m.P / 'phase04/run-witness-path.png'
    q.call('screendump', {'filename': str(shot), 'format': 'png'})
out.write_text(json.dumps(dict(phase=4, method='Observed Windows Run dialog, ordinary keyboard input',
    command='C:\\XWN404.EXE', keys=keys, typed_only=True, submitted=False,
    reason='RunOnce entry absent in phase3 cold hive after setup; original automatic handoff failed',
    screenshot=str(shot)), indent=2) + '\n')
print(shot)
