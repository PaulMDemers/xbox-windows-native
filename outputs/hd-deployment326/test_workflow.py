"""Actual deployment core against exact release bytes; FTP is an explicit in-memory model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import hd_overlay as h

ARCHIVE = Path('D:/Codex-archive/xbox-windows-native/0.2.0/xwn-0.2.0-hd-overlay.zip')
OUT = Path('D:/xwn326/host001')
REPORT = Path(__file__).with_name('host001.json')


class Remote:
    def __init__(self, data, fail_at=None, fault='before'):
        self.data = dict(data)
        self.writes = []
        self.fail_at = fail_at
        self.fault = fault

    def get(self, path):
        return self.data[path]

    def put(self, path, data):
        self.writes.append(path)
        if len(self.writes) == self.fail_at:
            self.fail_at = None
            if self.fault == 'after':
                self.data[path] = data
            elif self.fault == 'partial':
                self.data[path] = data[:len(data)//2]
            raise ConnectionError('Modeled transfer interruption')
        self.data[path] = data


def refuses(fn):
    try:
        fn()
    except (h.Refused, ConnectionError, PermissionError, FileExistsError):
        return
    raise AssertionError('Expected refusal')


def main():
    assert not REPORT.exists()
    OUT.mkdir(parents=True, exist_ok=False)
    package = h.Package(ARCHIVE, ROOT / 'tools/hd-overlay-0.2.0.json')
    before = {p: (ROOT / 'outputs/hd-physical324/artifacts/before001' / p.lstrip('/')).read_bytes()
              for p in package.baseline}
    assert package.identify(before) == 'baseline-restore'
    results = []

    def case(name, test):
        try:
            test(OUT / name)
            results.append({'name': name, 'passed': True})
        except BaseException as exc:
            results.append({'name': name, 'passed': False, 'error_type': type(exc).__name__})
            raise
        finally:
            h.save(REPORT, {'passed': all(r['passed'] for r in results), 'cases': results,
                            'transport': 'In-memory model; exact release payloads and actual core',
                            'physical_access': False,
                            'inputs': {str(p): h.sha(p.read_bytes()) for p in
                                       [Path(__file__), ROOT/'tools/hd_overlay.py', ROOT/'tools/deploy-hd.py',
                                        ROOT/'tools/hd-overlay-0.2.0.json']}})

    for incoming in h.PROFILES:
        for target in h.PROFILES:
            def success(path, incoming=incoming, target=target):
                data = dict(before); data.update(package.profiles[incoming])
                remote = Remote(data)
                h.prepare(remote, package, path, target)
                assert remote.writes == []
                h.apply(remote, package, path)
                assert package.identify(remote.data) == target
                refuses(lambda: h.apply(remote, package, path))
                if remote.writes: assert remote.writes[-1] == h.PATHS[-1]
                h.restore(remote, package, path)
                assert remote.data == data
                previous = list(remote.writes)
                h.restore(remote, package, path)
                assert remote.writes == previous  # An already restored receipt only verifies.
                refuses(lambda: h.prepare(remote, package, path, target))
            case(incoming+'-to-'+target, success)

    for fault in ['before', 'after', 'partial']:
        for index in range(1, 7):
            def interrupted(path, fault=fault, index=index):
                remote = Remote(before, index, fault)
                h.prepare(remote, package, path, '1080i')
                refuses(lambda: h.apply(remote, package, path))
                assert len(remote.writes) == index
                assert h.load(path/'transaction.json')['state'] == 'quarantined'
                if fault == 'partial':
                    count = len(remote.writes)
                    refuses(lambda: h.restore(remote, package, path))
                    assert len(remote.writes) == count
                    assert list((path/'unknown').iterdir())
                else:
                    h.restore(remote, package, path)
                    assert remote.data == before
            case(fault+str(index), interrupted)

    for index in range(1, 7):
        def restore_interruption(path, index=index):
            remote = Remote(before)
            h.prepare(remote, package, path, '1080i'); h.apply(remote, package, path)
            remote.fail_at = len(remote.writes) + index; remote.fault = 'after'
            refuses(lambda: h.restore(remote, package, path))
            h.restore(remote, package, path)
            assert remote.data == before
        case('restore-after'+str(index), restore_interruption)

    def mixed(path):
        remote = Remote(before); remote.data[h.PATHS[0]] = package.profiles['1080i'][h.PATHS[0]]
        refuses(lambda: h.prepare(remote, package, path, '1080i'))
        assert not remote.writes
    case('mixed-refused', mixed)

    for kind in ['hal', 'startup', 'preapply', 'backup', 'postapply-foreign']:
        def changed(path, kind=kind):
            remote = Remote(before)
            protected = next(p for p in before if p.endswith('/halxboxnt5.dll'))
            if kind == 'startup': protected = next(p for p in before if p.endswith('/xwnsetup.cmd'))
            if kind in ('hal', 'startup'):
                remote.data[protected] = b'changed'
                refuses(lambda: h.prepare(remote, package, path, '1080i'))
            else:
                h.prepare(remote, package, path, '1080i')
                if kind == 'preapply':
                    remote.data[protected] = b'changed'
                    refuses(lambda: h.apply(remote, package, path))
                elif kind == 'backup':
                    (path/'before'/h.PATHS[0].lstrip('/')).write_bytes(b'changed')
                    refuses(lambda: h.apply(remote, package, path))
                else:
                    h.apply(remote, package, path)
                    remote.data[h.PATHS[0]] = b'foreign'
                    count = len(remote.writes)
                    refuses(lambda: h.restore(remote, package, path))
                    assert len(remote.writes) == count
                    return
            assert not remote.writes
        case(kind+'-refused', changed)

    for stage in ['intent', 'commit']:
        def journal_failure(path, stage=stage):
            remote = Remote(before)
            h.prepare(remote, package, path, '1080i')
            original = h.save
            def fail(destination, record):
                if (stage == 'intent' and record['writes']) or (stage == 'commit' and record['state'] == 'committed'):
                    raise PermissionError('Modeled journal failure')
                return original(destination, record)
            with patch.object(h, 'save', fail): refuses(lambda: h.apply(remote, package, path))
            assert len(remote.writes) == (0 if stage == 'intent' else 6)
            h.restore(remote, package, path)
            assert remote.data == before
        case('journal-'+stage, journal_failure)

    def torn_archive(path):
        data = bytearray(ARCHIVE.read_bytes()); data[100] ^= 1
        path.mkdir(); bad = path/'bad.zip'; bad.write_bytes(data)
        refuses(lambda: h.Package(bad, ROOT/'tools/hd-overlay-0.2.0.json'))
    case('archive-byte-change', torn_archive)
    print(json.dumps({'passed': True, 'cases': len(results), 'physical_access': False}))


if __name__ == '__main__':
    main()
