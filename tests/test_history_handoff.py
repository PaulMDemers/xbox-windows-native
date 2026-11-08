import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'history-handoff.py'

class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.src = self.base / 'source'
        self.src.mkdir()
        (self.src / 'empty').mkdir()
        (self.src / 'file').write_text('hello', encoding='utf-8')
        self.manifest = self.base / 'manifest.jsonl'
        self.plan = self.base / 'plan.json'
        self.plan.write_text(json.dumps([{'source': str(self.src), 'destination': str(self.base / 'dest')}]))
    def tearDown(self):
        self.tmp.cleanup()
    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)
    def inventory(self):
        return self.run_tool('inventory', '--plan', self.plan, '--output', self.manifest)
    def verify(self):
        return self.run_tool('verify', '--manifest', self.manifest, '--location', 'source')
    def test_modified_and_missing(self):
        self.assertEqual(self.inventory().returncode, 0)
        self.assertEqual(self.verify().returncode, 0)
        (self.src / 'file').write_text('world', encoding='utf-8')
        self.assertNotEqual(self.verify().returncode, 0)
        (self.src / 'file').unlink()
        self.assertNotEqual(self.verify().returncode, 0)
    def test_link_refusal(self):
        try:
            (self.src / 'link').symlink_to(self.src / 'file')
        except OSError:
            self.skipTest('symlink creation unavailable')
        self.assertNotEqual(self.inventory().returncode, 0)
    def test_metadata_and_destination_inventory(self):
        result = self.run_tool('inventory', '--plan', self.plan, '--output', self.manifest, '--metadata-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.verify().returncode, 0)
        self.assertEqual(self.run_tool('verify', '--manifest', self.manifest, '--location', 'source', '--metadata-only').returncode, 0)
        self.src.rename(self.base / 'dest')
        self.assertEqual(self.run_tool('verify', '--manifest', self.manifest, '--location', 'destination', '--metadata-only').returncode, 0)
        full = self.base / 'full.jsonl'
        result = self.run_tool('inventory', '--plan', self.plan, '--output', full, '--location', 'destination')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.run_tool('verify', '--manifest', full, '--location', 'destination').returncode, 0)
    def test_long_path_and_rebase(self):
        import os
        long_root = str(self.src)
        if os.name == 'nt':
            long_root = '\\\\?\\' + long_root
        long_dir = Path(long_root)
        for n in range(5):
            long_dir = long_dir / (str(n) + 'x' * 65)
            long_dir.mkdir()
        (long_dir / 'content.txt').write_text('long path', encoding='utf-8')
        self.assertEqual(self.inventory().returncode, 0)
        self.assertEqual(self.verify().returncode, 0)
        moved = self.base / 'copy'
        self.src.rename(moved)
        result = self.run_tool('verify', '--manifest', self.manifest, '--location', 'source', '--rebase', self.src, moved)
        self.assertEqual(result.returncode, 0, result.stderr)
        cleanup = Path(('\\\\?\\' if os.name == 'nt' else '') + str(moved))
        for n in range(5):
            cleanup = cleanup / (str(n) + 'x' * 65)
        (cleanup / 'content.txt').unlink()
        for n in range(5):
            parent = cleanup.parent
            cleanup.rmdir()
            cleanup = parent
    def test_relative_escape_refusal(self):
        self.assertEqual(self.inventory().returncode, 0)
        rows = self.manifest.read_text().splitlines()
        record = json.loads(rows[1])
        record['path'] = '../escape'
        rows[1] = json.dumps(record)
        self.manifest.write_text('\n'.join(rows) + '\n')
        self.assertNotEqual(self.verify().returncode, 0)

if __name__ == '__main__':
    unittest.main()
