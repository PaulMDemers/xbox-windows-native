"""Content recovery and fail-closed tests; no real artifact removals."""
from compression import zstd
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('archiver', Path(__file__).with_name('archive-artifacts.py'))
archiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archiver)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sources = self.root / 'sources'
        self.dest = self.root / 'archive'
        self.sources.mkdir()
        self.dest.mkdir()
        self.reserve = patch.object(archiver, 'RESERVE', 0)
        self.reserve.start()

    def tearDown(self):
        self.reserve.stop()
        self.temp.cleanup()

    def item(self, name='trace.log', data=b'capture\x00\xff' * 10000):
        path = self.sources / name
        path.write_bytes(data)
        info = path.stat()
        return {'path': str(path), 'bytes': info.st_size, 'mtime_ns': info.st_mtime_ns}

    def test_compress_remove_restore(self):
        item = self.item()
        original = Path(item['path']).read_bytes()
        result = archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertFalse(Path(item['path']).exists())
        pointer = Path(item['path'] + '.archive-location.json')
        restored = self.sources / 'restored.log'
        archiver.restore(pointer, restored)
        self.assertEqual(restored.read_bytes(), original)
        self.assertLess(result['archive_bytes'], len(original))
        with self.assertRaises(FileExistsError):
            archiver.restore(pointer, restored)

    def test_existing_archive_identical_bytes(self):
        item = self.item('old.qcow2.zst', zstd.compress(b'private fixture' * 1000))
        original = Path(item['path']).read_bytes()
        result = archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertEqual(Path(result['archive']).read_bytes(), original)
        archiver.restore(Path(item['path'] + '.archive-location.json'), Path(item['path']))
        self.assertEqual(Path(item['path']).read_bytes(), original)

    def test_changed_source_refused(self):
        item = self.item()
        Path(item['path']).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertTrue(Path(item['path']).exists())

    def test_scope_and_raw_disk_refused(self):
        item = self.item()
        with self.assertRaises(ValueError):
            archiver.archive_one(item, [self.dest], self.dest, True)
        disk = self.item('disk.qcow2')
        with self.assertRaises(ValueError):
            archiver.archive_one(disk, [self.sources], self.dest, True)

    def test_invalid_zstd_keeps_source(self):
        item = self.item('invalid.zst', b'not a zstd archive')
        with self.assertRaises(zstd.ZstdError):
            archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertTrue(Path(item['path']).exists())
        self.assertFalse(Path(item['path'] + '.archive-location.json').exists())

    def test_corrupted_archive_refuses_restore(self):
        item = self.item()
        result = archiver.archive_one(item, [self.sources], self.dest)
        Path(result['archive']).write_bytes(b'corrupted')
        with self.assertRaises(RuntimeError):
            archiver.restore(Path(item['path'] + '.archive-location.json'), self.sources / 'restore.log')

    def test_mutation_during_verification_preserves_source(self):
        item = self.item()
        real = archiver.file_digest

        def mutate(path):
            if Path(path) == Path(item['path']):
                Path(path).write_bytes(b'new capture')
            return real(path)

        with patch.object(archiver, 'file_digest', side_effect=mutate):
            with self.assertRaises(RuntimeError):
                archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertEqual(Path(item['path']).read_bytes(), b'new capture')

    def test_failed_receipt_keeps_original(self):
        item = self.item()
        with patch.object(archiver, 'durable_json', side_effect=OSError('disk write failed')):
            with self.assertRaises(OSError):
                archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertTrue(Path(item['path']).exists())

    def test_low_space_keeps_original(self):
        item = self.item()
        with patch.object(archiver, 'RESERVE', 2**80):
            with self.assertRaises(RuntimeError):
                archiver.archive_one(item, [self.sources], self.dest, True)
        self.assertTrue(Path(item['path']).exists())
        self.assertFalse((self.dest / 'files').exists())


if __name__ == '__main__':
    unittest.main()
