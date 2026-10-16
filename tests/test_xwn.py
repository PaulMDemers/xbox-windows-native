# SPDX-License-Identifier: MIT
"""Exercise source/output guards without compilers or a console."""
import copy
import argparse
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('xwn', Path(__file__).resolve().parents[1] / 'tools/xwn.py')
xwn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xwn)


class Guards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.overlay = self.root / 'src/example'
        self.overlay.mkdir(parents=True)
        (self.overlay / 'code.c').write_bytes(b'/* original notice */\nint x;\n')
        self.profile = {'overlay': 'src/example', 'files': [
            {'path': 'code.c', 'action': 'write', 'mode': '100644',
             'sha256': xwn.digest(self.overlay / 'code.c')},
            {'path': 'obsolete.c', 'action': 'delete'}]}
        self.root_patch = patch.object(xwn, 'ROOT', self.root)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.tmp.cleanup()

    def test_traversal_rejected(self):
        for name in ['../outside', '/absolute', 'C:/absolute', 'a\\b', 'a/../../b', '']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                xwn.child(self.root, name)

    def test_unchanged_overlay(self):
        self.assertEqual(xwn.verify(self.profile), [])

    def test_changed_source_requires_explicit_development(self):
        (self.overlay / 'code.c').write_bytes(b'int different;\n')
        with self.assertRaises(ValueError):
            xwn.verify(self.profile)
        self.assertEqual(xwn.verify(self.profile, True), ['code.c'])

    def test_new_file_cannot_bypass_manifest(self):
        (self.overlay / 'new.c').write_text('int x;')
        with self.assertRaises(ValueError):
            xwn.verify(self.profile, True)

    def test_missing_source_rejected(self):
        (self.overlay / 'code.c').unlink()
        with self.assertRaises(ValueError):
            xwn.verify(self.profile, True)

    def test_unsupported_modes_and_actions(self):
        for field, value in [('mode', '120000'), ('action', 'copy-unchecked')]:
            p = copy.deepcopy(self.profile)
            p['files'][0][field] = value
            with self.assertRaises(ValueError):
                xwn.verify(p)

    def test_manifest_path_escape(self):
        p = copy.deepcopy(self.profile)
        p['files'][0]['path'] = '../../../other.c'
        with self.assertRaises(ValueError):
            xwn.verify(p)

    def test_output_protects_repo_cache_and_toolchain(self):
        for directory in ['repo', 'cache', 'toolchain']:
            anchor = self.root / directory
            anchor.mkdir()
            with self.assertRaises(ValueError):
                xwn.fresh(anchor / 'new-output', [anchor])

    def test_existing_output_never_reused(self):
        with self.assertRaises(ValueError):
            xwn.fresh(self.root, [])

    def test_fresh_sibling_allowed(self):
        self.assertEqual(xwn.fresh(self.root / 'output', [self.overlay]), self.root / 'output')

    def test_output_error_identifies_actual_protected_root(self):
        with self.assertRaises(ValueError) as caught:
            xwn.fresh(self.overlay / 'output', [self.root / 'unrelated', self.overlay])
        self.assertIn('protected root ' + str(self.overlay.resolve()), str(caught.exception))

    def test_empty_shell_paths_rejected(self):
        for value in ['', ' ', '\t']:
            with self.assertRaises(argparse.ArgumentTypeError):
                xwn.cli_path(value)
        self.assertEqual(xwn.cli_path('some path'), Path('some path'))

    def test_missing_rosbe_is_not_interpreted_as_parent_directory(self):
        tool = self.root / 'missing-rosbe'
        with self.assertRaisesRegex(ValueError, 'RosBE.sh'):
            xwn.toolchain_root(tool, 'reactos')
        tool.mkdir()
        with self.assertRaisesRegex(ValueError, 'RosBE.sh'):
            xwn.toolchain_root(tool, 'reactos')
        (tool / 'RosBE.sh').write_text('# bootstrap')
        self.assertEqual(xwn.toolchain_root(tool, 'reactos'), tool.resolve())

    def test_compiler_file_required(self):
        compiler = self.root / 'gcc-12'
        with self.assertRaises(ValueError):
            xwn.toolchain_root(compiler, 'cromwell')
        compiler.write_bytes(b'test placeholder')
        self.assertEqual(xwn.toolchain_root(compiler, 'cromwell'), self.root.resolve())


if __name__ == '__main__':
    unittest.main()
