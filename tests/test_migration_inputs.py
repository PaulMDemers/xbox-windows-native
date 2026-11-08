import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('migration_inputs', Path(__file__).resolve().parents[1] / 'tools/migration-inputs.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MigrationInputsTest(unittest.TestCase):
    def test_bind_verifies_and_remaps_then_refuses_corruption(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle = root / 'bundle'
            checkout = root / 'checkout'
            for p in (bundle / 'blobs', bundle / 'originals', checkout):
                p.mkdir(parents=True)
            data = b'pinned input'
            h = hashlib.sha256(data).hexdigest()
            (bundle / 'blobs' / h).write_bytes(data)
            record = b'record'
            rh = hashlib.sha256(record).hexdigest()
            (checkout / 'record.json').write_bytes(record)
            config = {'source_archive': 'old', 'source_sha256': h, 'overlays': [],
                      'source_records': [{'source': 'record.json', 'sha256': rh}]}
            (bundle / 'originals' / 'one.json').write_text(json.dumps(config))
            (bundle / 'originals' / m.F_HELPER).write_text('helper')
            (bundle / 'manifest.json').write_text(json.dumps({'inputs': {h: {'bytes': len(data)}}, 'originals': {'one.json': m.sha(bundle / 'originals' / 'one.json'), m.F_HELPER: m.sha(bundle / 'originals' / m.F_HELPER)}}))
            old = m.NAMES
            m.NAMES = ('one.json',)
            try:
                m.bind(bundle, checkout)
                derived = json.loads((bundle / 'recipes/one.json').read_text())
                self.assertEqual(derived['source_archive'], str(bundle / 'blobs' / h))
                self.assertEqual(derived['source_records'][0]['source'], str(checkout / 'record.json'))
                (checkout / 'record.json').write_bytes(b'changed')
                m.bind(bundle, checkout)
                self.assertIn('unavailable', json.loads((bundle / 'recipes/one.json').read_text()))
                (bundle / 'originals' / 'one.json').write_text('{}')
                with self.assertRaises(ValueError):
                    m.bind(bundle, checkout)
                (bundle / 'blobs' / h).write_bytes(b'corrupt')
                with self.assertRaises(ValueError):
                    m.bind(bundle, checkout)
            finally:
                m.NAMES = old

    def test_export_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                m.export(Path(td))


if __name__ == '__main__':
    unittest.main()
