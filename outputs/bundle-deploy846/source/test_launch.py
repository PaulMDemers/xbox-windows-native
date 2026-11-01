"""Host-only one-shot launch journal guards; never connects or sends SITE."""
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import contextmanager
import launch

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    args = SimpleNamespace(receipt=root)
    guard = root / 'global-launch-guard.jsonl'
    with patch.object(launch, 'LAUNCH_GUARD', guard):
        guard.write_text('{"kind":"intent"}\n')
        try:
            launch.validate(args)
        except ValueError as exc:
            assert 'never retry' in str(exc)
        else:
            raise AssertionError('Existing global launch guard accepted')
        guard.unlink()
        (root / 'launch846.jsonl').write_text('{"kind":"intent"}\n')
        try:
            launch.validate(args)
        except ValueError as exc:
            assert 'never retry' in str(exc)
        else:
            raise AssertionError('Existing local launch intent accepted')
    rows = {'/E/test': {'sha256': 'a' * 64}}
    good = [{'kind': 'write_intent', 'path': '/E/test', 'target_sha256': 'a' * 64},
            {'kind': 'write_verified', 'path': '/E/test', 'target_sha256': 'a' * 64}]
    assert launch.pairs(good, rows) == [('/E/test', 'a' * 64)]
    for bad in (good[:1], good + good):
        try:
            launch.pairs(bad, rows)
        except ValueError:
            pass
        else:
            raise AssertionError('Uncertain or duplicated writes accepted')
    (root / 'launch846.jsonl').unlink()
    data = b'mocked boot dependency'
    digest = launch.sha(data)
    path = 'E/test'
    pre = {'f_owner_marker': {'sha256': 'f' * 64}}
    fake_rows = {'/' + path: {'bytes': len(data)}}
    fake_targets = {'/' + path: {'target_path': '/' + path}}
    args = SimpleNamespace(receipt=root, config=root / 'config', dashboard_ip='192.168.50.242', journal_sha256='b' * 64)
    class FakeSocket:
        def settimeout(self, value):
            assert value == 20
    class FakeFTP:
        sock = FakeSocket()
        calls = 0
        def sendcmd(self, command):
            assert command == launch.COMMAND
            self.calls += 1
            raise TimeoutError('uncertain reply')
    ftp = FakeFTP()
    @contextmanager
    def lease(*_args, **_kwargs):
        yield ftp, '192.168.50.242'
    with patch.object(launch, 'LAUNCH_GUARD', guard), \
         patch.object(launch, 'PINS', {path: digest}), \
         patch.object(launch, 'validate', return_value=(pre, fake_rows, fake_targets, {'markers': []})), \
         patch.object(launch, 'deployment_lease', lease), \
         patch.object(launch, 'verify_f_owner', return_value={'sha256': 'f' * 64}), \
         patch.object(launch, 'retrieve', return_value=data):
        launch.run(args)
    assert ftp.calls == 1
    assert 'reply_uncertain' in guard.read_text() and 'reply_uncertain' in (root / 'launch846.jsonl').read_text()
    with patch.object(launch, 'LAUNCH_GUARD', guard):
        try:
            launch.validate(args)
        except ValueError as exc:
            assert 'never retry' in str(exc)
        else:
            raise AssertionError('Uncertain SITE was allowed to repeat')
print('846 host-only no-repeat launch and journal guards passed')
