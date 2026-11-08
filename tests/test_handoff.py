import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.write_bytes(b'synthetic preservation data')
        self.root = self.base / 'destination'
        self.plan = self.base / 'plan.json'
        self.write_plan('nested/data')

    def write_plan(self, destination):
        self.plan.write_text(json.dumps({'files': [{'source': str(self.source), 'destination': destination}]}), encoding='utf-8')

    def run_tool(self, name, *args):
        return subprocess.run([sys.executable, str(TOOLS / name), *map(str, args)], capture_output=True, text=True)

    def copy(self, *extra):
        return self.run_tool('save-handoff.py', self.plan, self.root, '--reserve-gib', '0', '--manifest', 'receipt.jsonl', *extra)

    def verify(self, *receipts):
        return self.run_tool('verify-handoff.py', self.root, *(receipts or ('receipt.jsonl',)))

    def test_copy_and_offline_verify(self):
        result = self.copy()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.source.unlink()
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Verified 1 files', result.stdout)

    def test_corruption_and_incomplete_receipt_fail(self):
        self.assertEqual(self.copy().returncode, 0)
        (self.root / 'nested/data').write_bytes(b'X' * self.source.stat().st_size)
        self.assertNotEqual(self.verify().returncode, 0)
        receipt = self.root / 'receipt.jsonl'
        receipt.write_text('\n'.join(receipt.read_text(encoding='utf-8').splitlines()[:-1]) + '\n', encoding='utf-8')
        self.assertNotEqual(self.verify().returncode, 0)

    def test_traversal_rejected_by_both_tools(self):
        self.write_plan('../escape')
        self.assertNotEqual(self.copy('--dry-run').returncode, 0)
        self.write_plan('nested/data')
        self.assertEqual(self.copy().returncode, 0)
        receipt = self.root / 'receipt.jsonl'
        records = [json.loads(line) for line in receipt.read_text(encoding='utf-8').splitlines()]
        records[1]['destination'] = '../escape'
        receipt.write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
        self.assertNotEqual(self.verify().returncode, 0)
        self.assertNotEqual(self.verify('../receipt.jsonl').returncode, 0)

    def test_conflicting_duplicate_receipts_fail(self):
        self.assertEqual(self.copy().returncode, 0)
        records = [json.loads(line) for line in (self.root / 'receipt.jsonl').read_text(encoding='utf-8').splitlines()]
        records[1]['sha256'] = '0' * 64
        (self.root / 'other.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
        self.assertNotEqual(self.verify('receipt.jsonl', 'other.jsonl').returncode, 0)


if __name__ == '__main__':
    unittest.main()
