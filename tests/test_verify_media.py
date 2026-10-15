# SPDX-License-Identifier: MIT
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('media', Path(__file__).resolve().parents[1] / 'tools/verify-media.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MediaIdentity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'any-name.iso'
        self.path.write_bytes(b'known-disc-content')
        self.row = {'id': 'disc', 'bytes': self.path.stat().st_size,
                    'sha256': hashlib.sha256(self.path.read_bytes()).hexdigest(),
                    'validation': {'status': 'hash-only', 'clean_install': False}}
        self.manifest = {'schema': 1, 'media': [self.row]}

    def test_match_does_not_upgrade_validation(self):
        r = m.identify(self.path, self.manifest)
        self.assertTrue(r['recognized'])
        self.assertFalse(r['validation']['clean_install'])

    def test_same_name_changed_bytes_rejected(self):
        self.path.write_bytes(b'changed-disc-bytes!')
        self.assertFalse(m.identify(self.path, self.manifest)['recognized'])

    def test_size_must_also_match(self):
        self.row['bytes'] += 1
        self.assertFalse(m.identify(self.path, self.manifest)['recognized'])

    def test_duplicate_and_unknown_schema_refuse(self):
        self.manifest['media'].append(dict(self.row))
        with self.assertRaises(ValueError):
            m.identify(self.path, self.manifest)
        self.manifest['schema'] = 2
        with self.assertRaises(ValueError):
            m.identify(self.path, self.manifest)


if __name__ == '__main__':
    unittest.main()
