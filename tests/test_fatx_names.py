# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from fatx_names import check_path, encode_component


class FatxNames(unittest.TestCase):
    def test_exact_oem_half_character(self):
        self.assertEqual(encode_component('3\u00bd Floppy (A).lnk',437),b'3\xab Floppy (A).lnk')

    def test_encoded_boundary(self):
        self.assertEqual(len(encode_component('\u00bd'*42,437)),42)
        with self.assertRaises(ValueError):encode_component('\u00bd'*43,437)

    def test_actual_crypto_and_sid_cannot_be_shortened(self):
        for value in ['S-1-5-21-1409082233-854245398-682003330-1000',
                      'fc1e3851f429ea606d6ff1e01a5229f1_9183439f-f927-4235-9436-6e19b14cb4ba',
                      '{02D4B3F1-FD88-11D1-960D-00805FC79235}.crmlog']:
            with self.assertRaises(ValueError):encode_component(value,437)

    def test_lossy_conversion_and_wrong_codepage_refused(self):
        for value in ['\u20ac','\U0001f600','\ud800']:
            with self.assertRaises(ValueError):encode_component(value,437)
        with self.assertRaises(ValueError):encode_component('file',1252)

    def test_path_escape_and_control_refused(self):
        for value in ['../file','/file','a//b','a/./b','a\\..\\b','C:/file','a\x00b','a\x1fb','a\x7fb']:
            with self.assertRaises(ValueError):check_path(value,437)
        self.assertEqual(check_path('folder\\file',437),[b'folder',b'file'])
