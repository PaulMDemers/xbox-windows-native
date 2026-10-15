# SPDX-License-Identifier: MIT
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('image_tool', Path(__file__).resolve().parents[1] / 'tools/xwn_image.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@unittest.skipUnless(os.name == 'posix', 'Linux flock is required')
class ImageGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.image = self.root / 'disk.raw'
        self.patches = [patch.object(m, 'SIZE', 32768), patch.object(m, 'START', 8192),
                        patch.object(m, 'LENGTH', 16384), patch.object(m, 'CHUNK', 1024)]
        for p in self.patches:
            p.start()
        b = bytearray(32768)
        b[8192:8196] = b'FATX'
        b[8200:8204] = (32).to_bytes(4, 'little')
        b[12288:16384] = bytes(range(256)) * 16
        self.original = bytes(b)
        self.image.write_bytes(b)

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def make_backup(self):
        out = self.root / 'backup'
        self.assertEqual(m.backup(self.image, out)['status'], 'verified')
        return out

    def test_actual_restore_and_outside_identity(self):
        bundle = self.make_backup()
        with self.image.open('r+b') as f:
            f.seek(13000)
            f.write(b'damaged-user-file')
        result = m.restore(self.image, bundle, self.root / 'restore')
        self.assertEqual(result['status'], 'verified')
        self.assertNotEqual(result['e_before'], result['e_after'])
        self.assertEqual(self.image.read_bytes(), self.original)

    def test_corrupt_compressed_and_uncompressed_hashes_refuse_before_write(self):
        bundle = self.make_backup()
        manifest = bundle / 'manifest.json'
        r = json.loads(manifest.read_text())
        for key in ['compressed_sha256', 'e_sha256', 'length', 'status']:
            changed = dict(r)
            changed[key] = 1 if key == 'length' else 'invalid'
            manifest.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                m.restore(self.image, bundle, self.root / ('bad-' + key))
            self.assertEqual(self.image.read_bytes(), self.original)

    def test_cross_image_outside_difference_refuses_without_writes(self):
        bundle = self.make_backup()
        b = bytearray(self.original)
        b[30000] = 7
        self.image.write_bytes(b)
        with self.assertRaises(ValueError):
            m.restore(self.image, bundle, self.root / 'refused')
        self.assertEqual(self.image.read_bytes(), b)
        self.assertFalse(json.loads((self.root / 'refused/restore.json').read_text())['writes_started'])

    def test_symlinks_rejected(self):
        link = self.root / 'link'
        link.symlink_to(self.image)
        with self.assertRaises(ValueError):
            m.backup(link, self.root / 'bad-link')
        directory = self.root / 'dir-link'
        directory.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            m.backup(directory / 'disk.raw', self.root / 'bad-parent')

    def test_geometry_and_partition_table_refused(self):
        for label, offset, value in [('table', 0, b'x'), ('fatx', 8192, b'bad!'), ('cluster', 8200, b'\x01')]:
            b = bytearray(self.original)
            b[offset:offset + len(value)] = value
            self.image.write_bytes(b)
            with self.assertRaises(ValueError):
                m.backup(self.image, self.root / label)
        self.image.write_bytes(self.original[:-1])
        with self.assertRaises(ValueError):
            m.backup(self.image, self.root / 'size')

    def test_existing_output_and_concurrent_image_refused(self):
        bundle = self.make_backup()
        with self.assertRaises(FileExistsError):
            m.backup(self.image, bundle)
        with m.image(self.image):
            with self.assertRaises(BlockingIOError):
                m.restore(self.image, bundle, self.root / 'locked')
        self.assertEqual(self.image.read_bytes(), self.original)

    def test_short_and_long_backup_rejected(self):
        import gzip
        for size in [m.LENGTH - 1, m.LENGTH + 1]:
            p = self.root / str(size)
            p.write_bytes(gzip.compress(bytes(size)))
            with self.assertRaises(ValueError):
                m.verify_payload(p, 'irrelevant')

    def test_interrupted_write_is_failed_and_explicit_new_receipt_can_recover(self):
        bundle = self.make_backup()
        b = bytearray(self.original)
        b[13000:13010] = b'0123456789'
        self.image.write_bytes(b)
        original = m.verify_payload
        def interrupted(path, expected, dest=None):
            if dest is None:
                return original(path, expected)
            dest.write(self.original[m.START:m.START + 1024])
            raise OSError('injected interrupted write')
        with patch.object(m, 'verify_payload', interrupted):
            with self.assertRaises(OSError):
                m.restore(self.image, bundle, self.root / 'partial')
        record = json.loads((self.root / 'partial/restore.json').read_text())
        self.assertEqual(record['status'], 'failed')
        self.assertTrue(record['writes_started'])
        self.assertNotEqual(self.image.read_bytes(), self.original)
        self.assertEqual(m.restore(self.image, bundle, self.root / 'explicit-retry')['status'], 'verified')
        self.assertEqual(self.image.read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
