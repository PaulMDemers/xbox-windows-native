# SPDX-License-Identifier: MIT
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import hardware_report as h


def example():
    return dict(schema=1, tool='xwn-hardware-report-1', kernel=[1,0,4627,1], hardware_flags=65,
        gpu_revision=163, mcp_revision=178, memory_status=0, kernel_total_pages=16384, page_bytes=4096,
        video_settings=260, av_pack=4, video_standard=256,
        encoder_probe=dict(label='conexant-response', conexant_status=0, conexant_value=0,
                           focus_status=3221225861, focus_value=0),
        e_space=dict(ok=True, free_bytes=4000000, total_bytes=5000000),
        available_32bit_modes=[[640,480,32,60]],
        pci=[dict(bus=1,device=0,function=0,id=44044510,class_revision=50331809)], complete=True)


class Inventory(unittest.TestCase):
    def test_valid_and_unknown_encoder(self):
        r=example(); self.assertEqual(h.validate(r),r)
        r['encoder_probe']['conexant_status']=1; r['encoder_probe']['label']='unidentified'
        h.validate(r)
        r['encoder_probe']['label']='xcalibur'
        with self.assertRaises(ValueError): h.validate(r)

    def test_rejects_private_injected_fields_and_invalid_ranges(self):
        for key,value in [('serial','private'),('schema',True),('complete',False),('gpu_revision',256),
                          ('memory_status',-1),('av_pack',0),('page_bytes',8192),('pci',[{}])]:
            r=example();r[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):h.validate(r)

    def test_duplicates_capacities_and_space(self):
        for key in ('pci','available_32bit_modes'):
            r=example();r[key]*=2
            with self.assertRaises(ValueError):h.validate(r)
        r=example();r['e_space']['free_bytes']=6000000
        with self.assertRaises(ValueError):h.validate(r)
        with self.assertRaises(ValueError):json.loads('{"schema":1,"schema":1}',object_pairs_hook=h.unique)

    def test_actual_parser_size_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'report.json';p.write_text(json.dumps(example()));self.assertEqual(h.load(p),example())
            p.write_bytes(b' '*32768)
            with self.assertRaises(ValueError):h.load(p)


if __name__ == '__main__':unittest.main()
