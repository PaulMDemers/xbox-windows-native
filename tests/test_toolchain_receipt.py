# SPDX-License-Identifier: MIT
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('receipt', Path(__file__).resolve().parents[1] / 'tools/toolchain_receipt.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ToolchainReceipt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.prefix = self.root / 'RosBE-2.2.1'
        self.prefix.mkdir()
        (self.prefix / 'gcc').write_bytes(b'compiler')
        (self.prefix / 'libgcc').write_bytes(b'library')
        self.lock = {'archives': {'rosbe': {'sha256': 'archive'}}, 'ninja_compatibility': {'patched_sha256': 'ninja'}}
        self.record = {'status': 'compiled', 'archive_sha256': 'archive', 'ninja_sha256': 'ninja',
                       'tool_sha256': {'gcc': m.sha(self.prefix / 'gcc')}}
        self.bootstrap = self.root / 'bootstrap.json'
        self.bootstrap.write_text(json.dumps(self.record))
        self.receipt = self.root / 'toolchain.json'

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_file_checked_including_libraries(self):
        m.create(self.bootstrap, self.receipt, self.lock)
        self.assertEqual(m.verify(self.prefix, self.receipt, self.lock)['files'], 2)
        (self.prefix / 'libgcc').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            m.verify(self.prefix, self.receipt, self.lock)

    def test_missing_and_extra_files_refused(self):
        m.create(self.bootstrap, self.receipt, self.lock)
        (self.prefix / 'extra').write_bytes(b'new')
        with self.assertRaises(ValueError):
            m.verify(self.prefix, self.receipt, self.lock)
        (self.prefix / 'extra').unlink()
        (self.prefix / 'libgcc').unlink()
        with self.assertRaises(ValueError):
            m.verify(self.prefix, self.receipt, self.lock)

    def test_failed_bootstrap_and_unknown_inputs_refused(self):
        for key in ['status', 'archive_sha256', 'ninja_sha256']:
            r = dict(self.record)
            r[key] = 'bad'
            self.bootstrap.write_text(json.dumps(r))
            with self.assertRaises(ValueError):
                m.create(self.bootstrap, self.receipt, self.lock)

    def test_changed_primary_tool_refuses_receipt_creation(self):
        (self.prefix / 'gcc').write_bytes(b'new')
        with self.assertRaises(ValueError):
            m.create(self.bootstrap, self.receipt, self.lock)

    @unittest.skipUnless(os.name == 'posix', 'symlink permissions vary on Windows')
    def test_external_and_broken_links_refused(self):
        link = self.prefix / 'link'
        for target in [self.bootstrap, self.prefix / 'missing']:
            link.symlink_to(target)
            with self.assertRaises(ValueError):
                m.inventory(self.prefix)
            link.unlink()


if __name__ == '__main__':
    unittest.main()
