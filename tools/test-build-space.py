"""Regression: a large virtual WSL disk must not mask a full Windows volume."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import build_space

checks = []
with patch.object(build_space.platform, 'release', return_value='microsoft-standard-WSL2'), \
     patch.dict(build_space.os.environ, {'WSL_DISTRO_NAME': "test'distro"}), \
     patch.object(build_space.shutil, 'disk_usage', return_value=SimpleNamespace(free=900*1024**3)), \
     patch.object(build_space.shutil, 'which', return_value='/mock/powershell.exe'):
    for free, expected in [(0, False), (30*1024**3, True)]:
        reply = json.dumps(dict(kind='WSL backing volume', path='C:\\', free_bytes=free)).encode()
        with patch.object(build_space.subprocess, 'check_output', return_value=reply) as proc:
            try:
                build_space.require_space(Path(__file__).parent)
                accepted = True
            except RuntimeError:
                accepted = False
            assert accepted == expected
            script = build_space.base64.b64decode(proc.call_args.args[0][-1]).decode('utf-16le')
            assert "-eq 'test''distro'" in script
            checks.append(dict(host_free_bytes=free, accepted=accepted, expected=expected))
    with patch.object(build_space.shutil, 'which', return_value=None):
        try:
            build_space.require_space(Path(__file__).parent)
            raise AssertionError('Unobservable host volume accepted')
        except RuntimeError:
            checks.append(dict(unobservable_host_rejected=True))
print(json.dumps(dict(passed=True, checks=checks), indent=2))
