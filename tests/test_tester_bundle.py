# SPDX-License-Identifier: MIT
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import tester_bundle as b


class Bundles(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup)
        self.base = Path(self.t.name); self.root = self.base/'stage'
        self.xbe = self.root/'E/Applications/XWNInfo/default.xbe'
        self.xbe.parent.mkdir(parents=True); self.xbe.write_bytes(b'test fixture only')
        self.m = b.collect(self.root, 'utilities'); self.plan = self.base/'plan.json'
        self.plan.write_text(json.dumps(self.m))

    def test_roundtrip_determinism_and_exclusive_creation(self):
        x = self.base/'one.zip'; y = self.base/'two.zip'
        self.assertEqual(b.build(self.root, self.plan, x), b.build(self.root, self.plan, y))
        self.assertEqual(b.verify(x)['files'], self.m['files'])
        with self.assertRaises(ValueError): b.build(self.root, self.plan, x)

    def test_changed_and_extra_staging_files_refused(self):
        self.xbe.write_bytes(b'changed')
        with self.assertRaises(ValueError): b.build(self.root, self.plan, self.base/'bad.zip')
        self.assertFalse((self.base/'bad.zip').exists())

    def test_paths_and_case_collisions(self):
        for name in ('../C/a', '/E/a', 'E/../a', 'C/a', 'E/Applications/Other/a',
                     'E/Applications/XWNInfo/a.', 'E/Applications/XWNInfo/'+'x'*43,
                     'E/Applications/XWNInfo/eeprom.bin', 'E/Applications/XWNInfo/a:b'):
            with self.subTest(name=name), self.assertRaises(ValueError): b.safe_path(name, 'utilities')
        m = copy.deepcopy(self.m); row = dict(m['files'][0]); row['path'] = row['path'].upper(); m['files'].append(row)
        with self.assertRaises(ValueError): b.validate_manifest(m)

    def test_archive_extra_member_and_changed_contents(self):
        x = self.base/'one.zip'; b.build(self.root, self.plan, x)
        with zipfile.ZipFile(x, 'a') as z: z.writestr('C/evil', b'bad')
        with self.assertRaises(ValueError): b.verify(x)
        y = self.base/'changed.zip'
        with zipfile.ZipFile(y, 'w') as z:
            z.writestr('MANIFEST.json', json.dumps(self.m)); z.writestr(self.m['files'][0]['path'], b'changed')
        with self.assertRaises(ValueError): b.verify(y)

    def test_private_payload_requires_complete_layout_and_explicit_flag(self):
        m = copy.deepcopy(self.m); m['kind']='windows-e-preview'; m['profile']='e-720p'
        with self.assertRaises(ValueError): b.validate_manifest(m)
        for name in (b.LAUNCHER, 'E/Applications/XWNEBoot/freeldr.sys', 'E/Applications/XWNEBoot/rosload.exe',
                     'E/winnt/system32/config/system', 'E/winnt/system32/ntoskrnl.exe'):
            p=self.root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b'fixture')
        self.xbe.unlink()
        self.xbe.parent.rmdir()
        m=b.collect(self.root,'windows-e-preview'); self.plan.write_text(json.dumps(m))
        with self.assertRaises(ValueError): b.build(self.root,self.plan,self.base/'private.zip')
        b.build(self.root,self.plan,self.base/'private.zip',private_windows=True)

    def test_duplicate_json_and_symlink(self):
        with self.assertRaises(ValueError): b.decode(b'{"schema":1,"schema":1}')
        p=self.root/'host/link'; p.parent.mkdir()
        try: p.symlink_to(self.xbe)
        except OSError: self.skipTest('Host does not permit symlinks')
        with self.assertRaises(ValueError): b.collect(self.root,'utilities')

    def test_empty_directories_preserved_and_collisions_rejected(self):
        (self.root/'docs/empty').mkdir(parents=True)
        m=b.collect(self.root,'utilities');self.plan.write_text(json.dumps(m))
        x=self.base/'dirs.zip';b.build(self.root,self.plan,x)
        with zipfile.ZipFile(x) as z:self.assertIn('docs/empty/',z.namelist())
        m['directories'].append('E/Applications/XWNInfo/default.xbe')
        with self.assertRaises(ValueError):b.validate_manifest(m)

    def test_manifest_claims_extra_fields_and_links(self):
        for field,value in [('schema',2),('schema',True),('qualification','PASS'),('console_target','C'),('profile','unknown'),('password','not-a-secret-fixture')]:
            m=copy.deepcopy(self.m);m[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):b.validate_manifest(m)
        x=self.base/'link-manifest.zip'
        with zipfile.ZipFile(x,'w') as z:
            i=zipfile.ZipInfo('MANIFEST.json');i.external_attr=(0o120777<<16)
            z.writestr(i,json.dumps(self.m))
        with self.assertRaises(ValueError):b.verify(x)

    def test_readback_exact_changed_and_extra(self):
        x=self.base/'readback.zip'; b.build(self.root,self.plan,x)
        self.assertEqual(b.verify_tree(x,self.root,console_only=True)['files'],1)
        self.xbe.write_bytes(b'damaged')
        with self.assertRaises(ValueError):b.verify_tree(x,self.root,console_only=True)
        self.xbe.write_bytes(b'test fixture only')
        (self.root/'E/unrelated').write_bytes(b'no')
        with self.assertRaises(ValueError):b.verify_tree(x,self.root,console_only=True)

    def test_deferred_launcher_readback(self):
        self.xbe.unlink(); self.xbe.parent.rmdir()
        for name in (b.LAUNCHER,'E/Applications/XWNEBoot/freeldr.sys','E/Applications/XWNEBoot/rosload.exe',
                     'E/winnt/system32/config/system','E/winnt/system32/ntoskrnl.exe'):
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'fixture')
        m=b.collect(self.root,'windows-e-preview');self.plan.write_text(json.dumps(m))
        x=self.base/'win.zip';b.build(self.root,self.plan,x,private_windows=True)
        launcher=self.root/b.LAUNCHER;launcher.unlink()
        result=b.verify_tree(x,self.root,console_only=True,defer_launcher=True)
        self.assertTrue(result['launcher_deferred']);self.assertEqual(result['files'],4)
        with self.assertRaises(ValueError):b.verify_tree(x,self.root,console_only=True)
        launcher.write_bytes(b'fixture');b.verify_tree(x,self.root,console_only=True)
        with self.assertRaises(ValueError):b.verify_tree(x,self.root,console_only=True,defer_launcher=True)


if __name__ == '__main__': unittest.main()
