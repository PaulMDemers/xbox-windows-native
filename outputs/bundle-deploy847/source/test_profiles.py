"""Offline package and mocked source-profile gates for 847; no console/network use."""
import datetime
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'outputs/bundle-deploy846/source'))
sys.path.insert(0, str(ROOT / 'tools'))
import tester_bundle
from common import sha
from profiles import expected_delta, pins, verify_archive, verify_source_profile, common_tree_digest
TRANSFER_SPEC = importlib.util.spec_from_file_location('transfer847', HERE / 'transfer.py')
transfer847 = importlib.util.module_from_spec(TRANSFER_SPEC)
TRANSFER_SPEC.loader.exec_module(transfer847)
LAUNCH_SPEC = importlib.util.spec_from_file_location('launch847', HERE / 'launch.py')
launch847 = importlib.util.module_from_spec(LAUNCH_SPEC)
LAUNCH_SPEC.loader.exec_module(launch847)


class MockFTP:
    def __init__(self, files, dirs):
        self.files = {p.casefold(): (p, b) for p, b in files.items()}
        self.dirs = {p.casefold(): p for p in dirs}
        self.cwd_path = None
        self.calls = []

    def cwd(self, path):
        self.calls.append(('CWD', path))
        assert path.casefold() in self.dirs
        self.cwd_path = self.dirs[path.casefold()]

    def pwd(self):
        self.calls.append(('PWD', self.cwd_path))
        return self.cwd_path.replace('/', '\\')

    def retrlines(self, command, callback):
        assert command == 'LIST'
        self.calls.append(('LIST', self.cwd_path))
        prefix = self.cwd_path.rstrip('/') + '/'
        entries = {}
        for p in self.dirs.values():
            if p.casefold().startswith(prefix.casefold()):
                tail = p[len(prefix):]
                if '/' not in tail:
                    entries[tail.casefold()] = (tail, True, 0)
        for p, data in self.files.values():
            if p.casefold().startswith(prefix.casefold()):
                tail = p[len(prefix):]
                if '/' not in tail:
                    entries[tail.casefold()] = (tail, False, len(data))
        for name, is_dir, size in entries.values():
            callback(f"{'d' if is_dir else '-'}rwxr-xr-x 1 xbox xbox {size} Jan 01 2000 {name}")

    def retrbinary(self, command, callback, blocksize):
        self.calls.append(('RETR', command[5:]))
        path = command[5:].casefold()
        assert path in self.files
        data = self.files[path][1]
        for off in range(0, len(data), blocksize):
            callback(data[off:off + blocksize])


class ProfileTests(unittest.TestCase):
    def test_archive_target_index_matches_receipt_absolute_paths(self):
        files = [
            {'path': 'E/Applications/XWNEBoot/default.xbe', 'bytes': 12, 'sha256': 'a' * 64},
            {'path': 'E/winnt/system32/drivers/xwnfatx.sys', 'bytes': 34, 'sha256': 'b' * 64},
            {'path': 'F/private-marker.json', 'bytes': 5, 'sha256': 'c' * 64},
        ]
        targets = {
            '/E/applications/xwneboot/default.xbe': {
                'kind': 'file', 'archive_path': files[0]['path'], 'expected_bytes': 12,
                'expected_sha256': 'a' * 64,
            },
            '/e/WINNT/system32/drivers/XWNFATX.SYS': {
                'kind': 'file', 'archive_path': files[1]['path'], 'expected_bytes': 34,
                'expected_sha256': 'b' * 64,
            },
            '/E/Applications/XWNEBoot': {'kind': 'directory', 'archive_path': 'E/Applications/XWNEBoot'},
        }
        rows, indexed = transfer847.index_archive_targets(files, targets)
        self.assertEqual(set(rows), {'/e/applications/xwneboot/default.xbe',
                                     '/e/winnt/system32/drivers/xwnfatx.sys'})
        self.assertEqual(set(rows), set(indexed))
        with self.assertRaisesRegex(ValueError, 'Incomplete archive target inventory'):
            transfer847.index_archive_targets(files, {next(iter(targets)): next(iter(targets.values()))})

    def test_shared_pin_lookup_is_case_insensitive_and_unambiguous(self):
        shared = {'E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd':
                  {'sha256': 'd' * 64}}
        self.assertEqual(transfer847.lookup_shared_pin(shared,
                                                       '/e/DOCUMENTS AND SETTINGS/ALL USERS/START MENU/PROGRAMS/STARTUP/XWNSETUP.CMD'),
                         {'sha256': 'd' * 64})
        with self.assertRaisesRegex(ValueError, 'missing or ambiguous'):
            transfer847.lookup_shared_pin(shared, '/E/missing.cmd')
        with self.assertRaisesRegex(ValueError, 'missing or ambiguous'):
            transfer847.lookup_shared_pin({**shared, next(iter(shared)).lower(): {'sha256': 'e' * 64}},
                                          '/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd')

    def test_both_target_archives_and_full_neutral_tree_are_pinned(self):
        table = pins()
        for profile in ('e-720x480', 'e-1080i'):
            archive = Path(table['profiles'][profile]['archive'].replace('/', '\\'))
            manifest, entry, _ = verify_archive(archive, profile)
            self.assertEqual(manifest['profile'], profile)
            count, digest = common_tree_digest(manifest)
            self.assertEqual(count, table['shared_tree']['file_count'])
            self.assertEqual(digest, table['shared_tree']['sha256'])
            self.assertEqual(entry['launcher']['sha256'], table['profiles'][profile]['launcher']['sha256'])

    def test_delta_is_exact_and_launcher_is_last(self):
        table = pins()
        p720 = Path(table['profiles']['e-720p']['archive'].replace('/', '\\'))
        p480 = Path(table['profiles']['e-720x480']['archive'].replace('/', '\\'))
        p1080 = Path(table['profiles']['e-1080i']['archive'].replace('/', '\\'))
        m720 = tester_bundle.verify(p720)
        m480, _, _ = verify_archive(p480, 'e-720x480')
        m1080, _, _ = verify_archive(p1080, 'e-1080i')
        self.assertEqual([x['kind'] for x in expected_delta('e-720p', 'e-720x480', m480)], ['launcher'])
        delta = expected_delta('e-720p', 'e-1080i', m1080)
        self.assertEqual([x['kind'] for x in delta], ['xwnfatx', 'launcher'])
        self.assertEqual(delta[-1]['path'], 'E/Applications/XWNEBoot/default.xbe')
        self.assertEqual(expected_delta('e-1080i', 'e-720p', m720)[-1]['after_sha256'],
                         table['profiles']['e-720p']['launcher']['sha256'])
        with self.assertRaisesRegex(ValueError, 'different supported fixed profile'):
            expected_delta('e-720x480', 'e-720x480', m480)

    def test_current_profile_check_ignores_user_data_but_rejects_startup_hook(self):
        table = pins(); profile = table['profiles']['e-720p']
        archive = Path(profile['archive'].replace('/', '\\'))
        with zipfile.ZipFile(archive) as z:
            selected = {}
            for key in ('launcher', 'xwnfatx'):
                item = profile[key]
                selected['/' + item['path']] = z.read(item['path'])
            for path, item in table['shared_boot_and_startup'].items():
                selected['/' + path] = z.read(path)
        # Unrelated changed user data is present, but current profile identity
        # depends only on known boot files and the normal startup surface.
        selected['/E/Documents and Settings/Win2K/My Documents/changed.txt'] = b'user changed data'
        dirs = {'/E'}
        for p in selected:
            parts = p.strip('/').split('/')[:-1]; cur='/' + parts[0]; dirs.add(cur)
            for part in parts[1:]: cur += '/' + part; dirs.add(cur)
        ftp = MockFTP(selected, dirs)
        state = verify_source_profile(ftp, 'e-720p', retrieve=__import__('common').retrieve,
                                      list_dir=__import__('preflight')._list_dir)
        self.assertEqual(state['profile'], 'e-720p')
        self.assertTrue(any(p.endswith('changed.txt') for p in selected))
        incomplete = dict(selected)
        incomplete['/E/winnt/system32/bootvid.dll'] = b'wrong boot video'
        dirs_incomplete = set(dirs)
        ftp_bad = MockFTP(incomplete, dirs_incomplete)
        with self.assertRaisesRegex(ValueError, 'Current profile pin mismatch'):
            verify_source_profile(ftp_bad, 'e-720p', retrieve=__import__('common').retrieve,
                                  list_dir=__import__('preflight')._list_dir)
        selected['/E/Documents and Settings/All Users/Start Menu/Programs/Startup/diagnostic.cmd'] = b'hook'
        parts='/E/Documents and Settings/All Users/Start Menu/Programs/Startup/diagnostic.cmd'.strip('/').split('/')[:-1]
        cur='/' + parts[0]; dirs.add(cur)
        for part in parts[1:]: cur += '/' + part; dirs.add(cur)
        ftp2 = MockFTP(selected, dirs)
        with self.assertRaisesRegex(ValueError, 'Unexpected startup command/hook'):
            verify_source_profile(ftp2, 'e-720p', retrieve=__import__('common').retrieve,
                                  list_dir=__import__('preflight')._list_dir)

    def test_profile_gate_rejects_other_revisions_and_profiles(self):
        with self.assertRaisesRegex(ValueError, 'Only fixed 480p or 1080i'):
            verify_archive(Path('unused'), 'e-640x480')

    def test_capacity_gate_requires_recent_conservative_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'capacity.json'
            obj = {'schema': 1, 'source': 'user-dashboard-observation', 'dashboard_ip': '192.168.50.242',
                   'volume': 'E', 'cluster_bytes': 16384,
                   'observed_utc': (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=25)).isoformat(),
                   'displayed_bytes': 1024*1024*1024, 'rounding_bytes': 16*1024, 'lower_bound_bytes': 1024*1024*1024-16*1024}
            raw = json.dumps(obj).encode(); path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'last 20 minutes'):
                transfer847.load_capacity(path, sha(raw), '192.168.50.242')

    def test_unique_profile_attempt_lock_blocks_replay(self):
        preflight = __import__('compat').preflight847()
        lock = preflight.STATE / 'e-720x480-lockcase.lock'
        with preflight.attempt_lock('e-720x480', 'lockcase'):
            self.assertTrue(lock.exists())
            with self.assertRaises(FileExistsError):
                with preflight.attempt_lock('e-720x480', 'lockcase'):
                    pass
            # Different target profiles/attempts do not alias the local lock name.
            with preflight.attempt_lock('e-1080i', 'lockcase'):
                self.assertTrue((preflight.STATE / 'e-1080i-lockcase.lock').exists())
        self.assertFalse(lock.exists())
        self.assertFalse((preflight.STATE / 'e-1080i-lockcase.lock').exists())

    def test_root_directory_lookup_is_case_insensitive(self):
        preflight = __import__('compat').preflight847()
        self.assertTrue(preflight.lookup_directory({'/E': {'exists': True}}, '/E')['exists'])
        self.assertTrue(preflight.lookup_directory({'/e': {'exists': True}}, '/E')['exists'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
