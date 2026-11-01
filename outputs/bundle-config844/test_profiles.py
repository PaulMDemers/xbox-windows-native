"""Small package round trips for the display profile labels; no Windows files."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import tester_bundle as b

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / 'stage'
    for path in (b.LAUNCHER, 'E/Applications/XWNEBoot/freeldr.sys',
                 'E/Applications/XWNEBoot/rosload.exe', 'E/WINNT/system32/config/system',
                 'E/WINNT/system32/ntoskrnl.exe'):
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'profile fixture')
    assert b.collect(root, 'windows-e-preview')['profile'] == 'e-720p'
    for profile in ('e-720p', 'e-1080i', 'e-720x480', 'e-640x480', 'e-1024x576'):
        m = b.collect(root, 'windows-e-preview', profile)
        plan = Path(tmp) / (profile + '.json')
        import json
        plan.write_text(json.dumps(m), encoding='utf-8')
        archive = Path(tmp) / (profile + '.zip')
        b.build(root, plan, archive, private_windows=True)
        assert b.verify(archive)['profile'] == profile
        b.verify_tree(archive, root)
    try:
        b.collect(root, 'windows-e-preview', 'unknown')
    except ValueError:
        pass
    else:
        raise AssertionError('Unknown profile accepted')
print('Legacy default, five profile round trips, and unknown rejection passed')
