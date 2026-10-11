"""Decode read-only pre-action observations and correlate exact helper targets."""
import hashlib, importlib.util, json, re, sys
from pathlib import Path

k = Path(__file__).resolve().parent
case = sys.argv[1]
assert case in ['emu001', 'emu002']
run = k.parents[1] / ('work/runs/nt5setup-' + case)
out = k / case
assert (run / 'cleanup.json').exists()
spec = importlib.util.spec_from_file_location('observer', k / 'analyze-observer.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = dict(physical_access=False, identified_live_setup=False, errors=[])
try:
    raw = (run / 'observer.log').read_bytes()
    parsed = module.analyze(raw)
    (out / 'observer-analysis.json').write_text(json.dumps(parsed, indent=2) + '\n')
    result['observer_sha256'] = hashlib.sha256(raw).hexdigest()
    result['samples_complete'] = parsed['completed']
    prefix = 'rundll32.exe newdev.dll,DevInstall '
    ids = re.findall(r'"((?:PCI|USB)\\\\[^"\n]+)"', (k / 'policy.h').read_text())
    ids = [s.replace('\\\\', '\\') for s in ids]
    assert len(ids) == 6
    present = set()
    identified = []
    for sample in parsed['samples']:
        present.update(d['instance'].lower() for d in sample['devices'])
        for process in sample['processes']:
            command = process.get('command_utf16', '')
            if not command.lower().startswith(prefix.lower()):
                continue
            instance = command[len(prefix):]
            device = next((d for d in sample['devices'] if d['instance'].lower() == instance.lower()), None)
            windows = [w for w in sample['windows'] if w['pid'] == process['pid']]
            titles = [w for w in windows if w['kind'] == 'TOP' and w.get('window_text') == 'Found New Hardware Wizard' and w['visible'] and w['enabled'] and w['text_query_ok']]
            texts = {w.get('window_text', '') for w in windows if w['visible'] and w['text_query_ok']}
            welcome = {'Welcome to the Found New Hardware Wizard', 'This wizard helps you install a device driver for a hardware device.', 'To continue, click Next.'} <= texts
            identified.append(dict(sample=sample['index'], pid=process['pid'], command=command, instance=instance, device=device, windows=windows, visible_welcome=bool(titles and welcome)))
    result['installers'] = identified
    result['helper_actions'] = []
    for line in (run / 'wizard201.log').read_text().splitlines():
        if line.startswith('CANCEL_SENT '):
            _, pid, hwnd, target = line.split()
            target = int(target)
            assert 1 <= target <= len(ids)
            result['helper_actions'].append(dict(pid=int(pid), hwnd=int(hwnd), target=target, instance=ids[target-1], present_before_action=ids[target-1].lower() in present))
    result['identified_live_setup'] = bool(
        parsed['completed'] and any(v['device'] and v['visible_welcome'] for v in identified)
        and result['helper_actions'] and all(v['present_before_action'] for v in result['helper_actions']))
except (OSError, ValueError, AssertionError, KeyError) as error:
    result['errors'].append(repr(error))
result['limits'] = 'Observer precedes helper. Helper separately revalidates full command, process creation identity and exact active welcome/Cancel controls immediately before action. Present device metadata is not driver support. Query failures remain in observer-analysis.json.'
(out / 'setup-evidence.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({n:v for n,v in result.items() if n != 'installers'}))
