"""Offline mocked tests for the 846 1.0 preflight; no network or console access."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('preflight846', HERE / 'preflight.py')
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)
from common import F_OWNER_VALUE, load_private_config, sha
import tester_bundle as bundle

OWNER_BYTES = json.dumps(dict(attempt='642physical001', probe_case=642, mode='720x480p32',
                              ordinary720p_preserved=True), sort_keys=True).encode()
OWNER_SHA = 'd2793955b722c56828ba2a82e6a09c5d382fc98835dd4d2487f32927dddfed6f'
STAGE = preflight.ROOT / 'outputs/windows480p642/stage001.json'
STAGE_SHA = 'abbe3c386a514dc816a3b20199f09268c1f37d6d309939d15ed02cf35634af39'


class MemoryFTP:
    def __init__(self, files, directories, reported_sizes=None):
        self.files = {p.casefold(): (p, b) for p, b in files.items()}
        self.directories = {p.casefold(): p for p in directories}
        self.reported_sizes = {p.casefold(): n for p, n in (reported_sizes or {}).items()}
        self.current = None
        self.calls = []
        self.closed = False

    def connect(self, host, timeout):
        self.calls.append(('CONNECT', host))
        assert timeout == 15

    def login(self, user, password):
        self.calls.append(('LOGIN', user))
        assert user == 'dummy'
        assert password == 'not-a-real-secret'

    def cwd(self, path):
        self.calls.append(('CWD', path))
        assert path.casefold() in self.directories, path
        self.current = self.directories[path.casefold()]

    def pwd(self):
        self.calls.append(('PWD', self.current))
        return self.current.replace('/', '\\')

    def retrlines(self, command, callback):
        self.calls.append(('LIST', self.current))
        assert command == 'LIST'
        prefix = self.current.rstrip('/') + '/'
        entries = {}
        for path in self.directories.values():
            if path.casefold().startswith(prefix.casefold()):
                tail = path[len(prefix):]
                if '/' not in tail:
                    entries[tail.casefold()] = (tail, True, 0)
        for path, data in self.files.values():
            if path.casefold().startswith(prefix.casefold()):
                tail = path[len(prefix):]
                if '/' not in tail:
                    size = self.reported_sizes.get(path.casefold(), len(data))
                    entries[tail.casefold()] = (tail, False, size)
        for name, is_dir, size in entries.values():
            mode = 'drwxr-xr-x' if is_dir else '-rw-r--r--'
            callback(f'{mode} 1 xbox xbox {size} Jan 01 2000 {name}')

    def retrbinary(self, command, callback, blocksize):
        self.calls.append(('RETR', command[5:]))
        assert command.startswith('RETR ')
        path = command[5:].casefold()
        assert path in self.files, path
        data = self.files[path][1]
        for offset in range(0, len(data), blocksize):
            callback(data[offset:offset + blocksize])

    def close(self):
        self.closed = True

    def storbinary(self, *args, **kwargs):
        raise AssertionError('Preflight must never upload')

    def mkd(self, *args, **kwargs):
        raise AssertionError('Preflight must never create console paths')

    def delete(self, *args, **kwargs):
        raise AssertionError('Preflight must never delete console paths')

    def sendcmd(self, *args, **kwargs):
        raise AssertionError('Preflight must never issue SITE/launch commands')


def build_archive(folder: Path):
    root = folder / 'tree'
    files = {
        'E/Applications/XWNEBoot/default.xbe': b'new-720p-launcher',
        'E/Applications/XWNEBoot/freeldr.sys': b'freeldr',
        'E/Applications/XWNEBoot/rosload.exe': b'rosload',
        'E/WINNT/system32/ntoskrnl.exe': b'kernel',
        'E/WINNT/system32/config/system': b'hive',
        'E/Documents and Settings/Win2K/Desktop/readme.txt': b'doc',
        'E/Program Files/Example/app.exe': b'app',
        'E/xwndemo372/display-settings.exe': b'display',
    }
    for rel, data in files.items():
        p = root / Path(*rel.split('/'))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    manifest = bundle.collect(root, 'windows-e-preview', 'e-720p')
    manifest_file = folder / 'manifest.json'
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    archive = folder / 'xbox10-720p.zip'
    bundle.build(root, manifest_file, archive, private_windows=True)
    return archive, manifest


def make_identity(folder: Path, revision='1.0', ip='192.168.50.242'):
    obj = {
        'schema': 1, 'console_revision': revision, 'profile': 'e-720p', 'dashboard_ip': ip,
        'markers': [
            {'path': '/E/Applications/XWN480p642/owner.json', 'sha256': OWNER_SHA,
             'evidence_path': 'outputs/windows480p642/stage001.json', 'evidence_sha256': STAGE_SHA},
            {'path': '/E/xwn480p642/owner.json', 'sha256': OWNER_SHA,
             'evidence_path': 'outputs/windows480p642/stage001.json', 'evidence_sha256': STAGE_SHA},
        ],
    }
    path = folder / 'identity.json'
    data = json.dumps(obj, sort_keys=True).encode()
    path.write_bytes(data)
    return path, sha(data)


def fixture_target():
    files = {
        '/E/Applications/XWNEBoot/Default.XBE': b'old launcher',
        '/E/Applications/XWNEBoot/freeldr.sys': b'prior free loader',
        '/E/Applications/XWNEBoot/rosload.exe': b'prior rosload',
        '/E/WINNT/system32/ntoskrnl.exe': b'prior kernel',
        '/E/WINNT/system32/config/system': b'prior hive',
        '/E/WINNT/system32/extra.bin': b'extra managed file',
        '/E/Documents and Settings/Win2K/Desktop/readme.txt': b'old document',
        '/E/Documents and Settings/Win2K/Desktop/user-extra.txt': b'private extra',
        '/E/Program Files/Example/app.exe': b'old app',
        '/E/xwndemo372/display-settings.exe': b'old settings',
        '/E/Applications/XWN480p642/owner.json': OWNER_BYTES,
        '/E/xwn480p642/owner.json': OWNER_BYTES,
        '/F/xwn-deploy-v1.json': json.dumps(F_OWNER_VALUE).encode(),
        '/E/Unrelated-Large-Game.iso': b'x',
    }
    directories = {'/E', '/F'}
    for path in files:
        parts = path.strip('/').split('/')[:-1]
        cur = '/' + parts[0]
        directories.add(cur)
        for part in parts[1:]:
            cur += '/' + part
            directories.add(cur)
    return files, directories


class PreflightTests(unittest.TestCase):
    def test_private_session_is_ast_parsed_without_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'session.py'
            path.write_text("import os\nos.environ.update(XWN_FTP_HOST='192.168.50.242', XWN_FTP_USER='dummy', XWN_FTP_PASSWORD='not-a-real-secret')\nraise RuntimeError('must not run')\n")
            config = load_private_config(path)
            self.assertEqual(config['host'], '192.168.50.242')
            self.assertEqual(config['user'], 'dummy')
            self.assertEqual(config['password'], 'not-a-real-secret')

    def test_populated_multilevel_tree_case_mapping_extra_files_and_readonly(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp); (t / 'receipts').mkdir()
            archive, manifest = build_archive(t)
            identity, identity_sha = make_identity(t)
            cfg = t / 'private.json'
            cfg.write_text(json.dumps({'host': '192.168.50.242', 'user': 'dummy', 'password': 'not-a-real-secret'}))
            files, dirs = fixture_target()
            fake = MemoryFTP(files, dirs, {'/E/Unrelated-Large-Game.iso': 805306368})
            receipt_path = t / 'receipts' / 'run001'
            result = preflight.run(archive, sha(archive.read_bytes()), identity, identity_sha,
                                   cfg, '192.168.50.242', receipt_path,
                                   ftp_factory=lambda: fake, lock_path=t/'lease.lock',
                                   ticket_check=lambda: None,
                                   disk_usage_fn=lambda _: SimpleNamespace(free=40 * 1024**3))
            self.assertTrue(result['completed'])
            self.assertFalse(result['physical_writes'])
            self.assertFalse(result['launch_requested'])
            self.assertEqual(result['capacity']['status'], 'insufficient-evidence')
            self.assertEqual(fake.calls[0], ('CONNECT', '192.168.50.242'))
            self.assertNotIn(('RETR', '/E/Unrelated-Large-Game.iso'), fake.calls)
            self.assertIn('/E/Applications/XWNEBoot/Default.XBE', result['files'])
            self.assertEqual(result['archive_targets']['/E/Applications/XWNEBoot/default.xbe']['kind'], 'file')
            target = result['archive_targets']['/E/Applications/XWNEBoot/default.xbe']
            self.assertEqual(target['target_path'], '/E/Applications/XWNEBoot/Default.XBE')
            self.assertEqual(target['before_sha256'], sha(b'old launcher'))
            self.assertEqual(target['expected_sha256'], next(r['sha256'] for r in manifest['files']
                                                              if r['path'].endswith('default.xbe')))
            self.assertEqual(result['archive_targets']['/E/Applications']['kind'], 'directory')
            self.assertTrue(result['archive_targets']['/E']['exists'])
            self.assertEqual(result['archive_targets']['/E']['target_path'], '/E')
            self.assertTrue(result['directories']['/E']['exists'])
            self.assertIn('/E/WINNT/system32/extra.bin', result['files'])
            self.assertIn('/E/Documents and Settings/Win2K/Desktop/user-extra.txt', result['files'])
            self.assertTrue(all(call[0] in {'CONNECT', 'LOGIN', 'CWD', 'PWD', 'LIST', 'RETR'} for call in fake.calls))
            self.assertTrue(fake.closed)
            self.assertFalse((t / 'lease.lock').exists())
            self.assertNotIn('password', (receipt_path / 'preflight.json').read_text(encoding='utf-8').lower())

    def test_unrelated_large_root_file_is_listed_but_never_downloaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp); (t / 'receipts').mkdir()
            archive, _ = build_archive(t); identity, identity_sha = make_identity(t)
            cfg = t / 'private.json'; cfg.write_text(json.dumps({'host':'192.168.50.242','user':'dummy','password':'not-a-real-secret'}))
            files, dirs = fixture_target()
            fake = MemoryFTP(files, dirs, {'/E/Unrelated-Large-Game.iso': 805306368})
            preflight.run(archive, sha(archive.read_bytes()), identity, identity_sha, cfg, '192.168.50.242',
                          t/'receipts'/'run', ftp_factory=lambda: fake, lock_path=t/'lock',
                          ticket_check=lambda: None, disk_usage_fn=lambda _: SimpleNamespace(free=40*1024**3))
            self.assertFalse(any(c == ('RETR', '/E/Unrelated-Large-Game.iso') for c in fake.calls))

    def test_refuses_revision_16_before_connect(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp); archive, _ = build_archive(t); identity, identity_sha = make_identity(t, revision='1.6')
            cfg = t/'private.json'; cfg.write_text(json.dumps({'host':'192.168.50.242','user':'dummy','password':'x'}))
            fake = MemoryFTP({}, {'/E','/F'})
            with self.assertRaisesRegex(ValueError, 'revision other than Xbox 1.0'):
                preflight.run(archive, sha(archive.read_bytes()), identity, identity_sha, cfg, '192.168.50.242',
                              t/'missing', ftp_factory=lambda: fake, lock_path=t/'lock', ticket_check=lambda: None)
            self.assertEqual(fake.calls, [])

    def test_rejects_16_endpoint_before_connect(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp); archive,_=build_archive(t); identity,identity_sha=make_identity(t,ip='192.168.50.66')
            cfg=t/'private.json';cfg.write_text(json.dumps({'host':'192.168.50.66','user':'dummy','password':'x'}))
            fake=MemoryFTP({}, {'/E','/F'})
            with self.assertRaisesRegex(ValueError, 'allowlist'):
                preflight.run(archive,sha(archive.read_bytes()),identity,identity_sha,cfg,'192.168.50.66',t/'missing',
                              ftp_factory=lambda:fake,lock_path=t/'lock',ticket_check=lambda:None)
            self.assertEqual(fake.calls,[])

    def test_rejects_marker_mismatch_before_tree_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp);(t/'receipts').mkdir();archive,_=build_archive(t);identity,identity_sha=make_identity(t)
            cfg=t/'private.json';cfg.write_text(json.dumps({'host':'192.168.50.242','user':'dummy','password':'not-a-real-secret'}))
            files,dirs=fixture_target();files['/E/Applications/XWN480p642/owner.json']=b'wrong owner'
            fake=MemoryFTP(files,dirs)
            with self.assertRaisesRegex(ValueError,'identity marker hash mismatch'):
                preflight.run(archive,sha(archive.read_bytes()),identity,identity_sha,cfg,'192.168.50.242',t/'receipts'/'run',
                              ftp_factory=lambda:fake,lock_path=t/'lock',ticket_check=lambda:None,
                              disk_usage_fn=lambda _:SimpleNamespace(free=40*1024**3))
            self.assertFalse((t/'receipts'/'run').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
