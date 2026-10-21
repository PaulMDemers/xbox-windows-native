"""SPDX-License-Identifier: MIT
Failure-injection tests of the real selector; no hardware or FTP connection.
Run: python -B -m unittest discover -s tests -p test_e_display_selector.py -v
"""
import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('selector', ROOT / 'tools/configure-e-display.py')
selector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)


class MemoryFTP:
    def __init__(self, files):
        self.files = dict(files)
        self.commands = []
        self.writes = 0
        self.fail_writes = set()
        self.corrupt_after_write = False
        self.after_read = None

    def retrbinary(self, command, callback, blocksize):
        op, path = command.split(' ', 1)
        assert op == 'RETR' and path in selector.ALLOWED
        self.commands.append(command)
        callback(self.files[path])
        if self.after_read:
            self.after_read(path)

    def storbinary(self, command, stream, blocksize):
        op, path = command.split(' ', 1)
        assert op in ('STOR', 'APPE') and path == selector.TARGET
        self.commands.append(command)
        self.writes += 1
        data = stream.read()
        self.files[path] = (self.files[path] if op == 'APPE' else b'') + data
        if self.corrupt_after_write:
            self.corrupt_after_write = False
            self.files[path] = b'corrupt' + self.files[path]
        if self.writes in self.fail_writes:
            raise OSError('Injected failure after remote mutation')


class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.launchers = {'480p': b'low' * 40000, '720p': b'high' * 30000,
                          '1080i': b'interlace' * 15000}
        pin = lambda data: {'bytes': len(data), 'sha256': selector.sha(data)}
        prerequisites = {p: p.encode() for p in selector.ALLOWED - {selector.TARGET}}
        self.policy = {'target': selector.TARGET,
                       'prerequisites': {p: pin(b) for p, b in prerequisites.items()},
                       'profiles': {p: pin(b) for p, b in self.launchers.items()}}
        self.ftp = MemoryFTP({**prerequisites, selector.TARGET: self.launchers['720p']})
        self.receipt = self.root / 'receipt'

    def tearDown(self):
        self.temp.cleanup()

    def apply_low(self):
        return selector.apply(self.ftp, self.policy, '480p', self.launchers['480p'], self.receipt)

    def test_roundtrip_exact_backup_and_restore(self):
        result = self.apply_low()
        self.assertTrue(result['no_boot'])
        self.assertEqual((self.receipt / 'before.xbe').read_bytes(), self.launchers['720p'])
        self.assertEqual(self.ftp.files[selector.TARGET], self.launchers['480p'])
        selector.restore(self.ftp, self.policy, self.receipt)
        self.assertEqual(self.ftp.files[selector.TARGET], self.launchers['720p'])
        with self.assertRaises(ValueError):
            selector.restore(self.ftp, self.policy, self.receipt)

    def test_legacy_package_still_supported(self):
        del self.policy['profiles']['480p']
        self.assertEqual(selector.inspect(self.ftp, self.policy)[0], '720p')
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertEqual(self.ftp.writes, 0)

    def test_no_default_change_or_write_for_current_profile(self):
        selector.apply(self.ftp, self.policy, '720p', self.launchers['720p'], self.receipt)
        self.assertEqual(self.ftp.writes, 0)

    def test_bad_local_binary_refused_before_contact(self):
        with self.assertRaises(ValueError):
            selector.apply(self.ftp, self.policy, '480p', b'wrong', self.receipt)
        self.assertEqual(self.ftp.commands, [])

    def test_bad_prerequisite_refuses_write(self):
        self.ftp.files[next(iter(self.policy['prerequisites']))] = b'wrong'
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertEqual(self.ftp.writes, 0)

    def test_unknown_current_refuses_write(self):
        self.ftp.files[selector.TARGET] = b'unknown'
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertEqual(self.ftp.writes, 0)

    def test_existing_receipt_preserved(self):
        self.receipt.mkdir()
        (self.receipt / 'marker').write_text('keep')
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertEqual((self.receipt / 'marker').read_text(), 'keep')
        self.assertEqual(self.ftp.writes, 0)

    def test_interrupted_first_or_append_write_rolls_back(self):
        for failure in (1, 2, 3, 4):
            with self.subTest(write=failure):
                self.ftp.files[selector.TARGET] = self.launchers['720p']
                self.ftp.writes = 0
                self.ftp.fail_writes = {failure}
                self.receipt = self.root / ('failure-' + str(failure))
                with self.assertRaises(OSError):
                    self.apply_low()
                self.assertEqual(self.ftp.files[selector.TARGET], self.launchers['720p'])
                self.assertTrue(selector.read_json(self.receipt / 'result.json')['rollback_verified'])

    def test_bad_transfer_readback_rolls_back(self):
        self.ftp.corrupt_after_write = True
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertEqual(self.ftp.files[selector.TARGET], self.launchers['720p'])

    def test_failed_rollback_retains_backup_and_reports_failure(self):
        self.ftp.fail_writes = {1, 2}
        with self.assertRaises(OSError):
            self.apply_low()
        result = selector.read_json(self.receipt / 'result.json')
        self.assertFalse(result['rollback_verified'])
        self.assertEqual(result['restore_error'], 'OSError')
        self.assertEqual((self.receipt / 'before.xbe').read_bytes(), self.launchers['720p'])
        self.ftp.fail_writes.clear()
        before = self.ftp.writes
        # A damaged launcher is not automatically overwritten on a later call.
        with self.assertRaises(ValueError):
            selector.restore(self.ftp, self.policy, self.receipt)
        self.assertEqual(self.ftp.writes, before)

    def test_change_between_inspection_and_write_refused(self):
        def replace(path):
            if path == selector.TARGET:
                self.ftp.files[path] = self.launchers['1080i']
                self.ftp.after_read = None
        self.ftp.after_read = replace
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertEqual(self.ftp.writes, 0)

    def test_change_after_store_verification_not_reported_as_success(self):
        reads = [0]
        def replace(path):
            if path == selector.TARGET:
                reads[0] += 1
                if reads[0] == 3:  # store's readback, before apply's final readback
                    self.ftp.files[path] = b'changed'
                    self.ftp.after_read = None
        self.ftp.after_read = replace
        with self.assertRaises(ValueError):
            self.apply_low()
        self.assertFalse(selector.read_json(self.receipt / 'result.json')['applied'])
        self.assertEqual(self.ftp.files[selector.TARGET], self.launchers['720p'])

    def test_tampered_backup_or_intervening_profile_blocks_restore(self):
        self.apply_low()
        self.ftp.files[selector.TARGET] = self.launchers['1080i']
        before = self.ftp.writes
        with self.assertRaises(ValueError):
            selector.restore(self.ftp, self.policy, self.receipt)
        self.ftp.files[selector.TARGET] = self.launchers['480p']
        (self.receipt / 'before.xbe').write_bytes(b'wrong')
        with self.assertRaises(ValueError):
            selector.restore(self.ftp, self.policy, self.receipt)
        self.assertEqual(self.ftp.writes, before)

    def test_duplicate_or_extra_profile_rejected(self):
        bad = copy.deepcopy(self.policy)
        bad['profiles']['480p'] = bad['profiles']['720p']
        with self.assertRaises(ValueError):
            selector.inspect(self.ftp, bad)
        self.policy['profiles']['576p'] = self.policy['profiles']['480p']
        with self.assertRaises(ValueError):
            selector.inspect(self.ftp, self.policy)
        self.assertEqual(self.ftp.commands, [])

    def test_other_paths_refused_before_contact(self):
        for path in ('/C/config.xml', '/F/default.xbe', '/E/../C/default.xbe'):
            with self.assertRaises(ValueError):
                selector.fetch(self.ftp, path)
        self.assertEqual(self.ftp.commands, [])

    def test_committed_policy_uses_qualified_candidate(self):
        policy = selector.read_json(ROOT / 'tools/e-display-policy.json')
        selector.validate_policy(policy)
        self.assertEqual(policy['profiles']['480p'], {
            'bytes': 300912,
            'sha256': 'a53a09427f80411efee73ef53da0ec9829f8af0d27d404f5a3ff818e96b4bde4'})


if __name__ == '__main__':
    unittest.main()
