# SPDX-License-Identifier: MIT
"""Independent receipt examples: boundaries, clocks, missing and forged telemetry."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import graphics_scenebench as b


def example():
    f = dict(schema='xwn-scene-bench-1', backend='default',
             scope='three-child-processes-including-pauses-and-capture-io',
             iterations='3', poll_ms='50', child_deadline_ms='50000',
             completed='3', exit='0', end='complete')
    f.update({'os.major':'5','os.minor':'0','os.build':'2195',
              'psapi.load':'1','psapi.entry':'1','psapi.unload':'1'})
    for i in range(3):
        values = dict(available_before=30000000, physical_total=67108864,
                      start_tick=(0xfffff000+i*12000)&0xffffffff,pid=120+i*4,
                      elapsed_ms=11000,wait=0,exit=0,samples=200,
                      min_ws=1000000,max_ws=2000000,peak_ws=2100000,
                      max_commit=3000000,peak_commit=3100000,
                      first_faults=10,last_faults=100,handles_closed=1,
                      available_after=29000000,complete=1)
        values.update({'created.high':10,'created.low':i*120000000+1,
                       'ended.high':10,'ended.low':i*120000000+110000001,
                       'kernel.high':0,'kernel.low':5000000,
                       'user.high':0,'user.low':15000000})
        f.update({f'c{i}.{k}':str(v) for k,v in values.items()})
    return f


def raw(f):
    return ''.join(k+'='+v+'\r\n' for k,v in f.items()).encode('ascii')


class TestBench(unittest.TestCase):
    def test_known_cost_and_tick_wrap(self):
        r=b.validate_report(raw(example()),'default',0)
        self.assertEqual(len(r['rows']),3)
        self.assertEqual(r['rows'][1]['user_ms'],1500)
        self.assertEqual(r['rows'][0]['sampled_page_fault_delta'],90)

    def test_missing_and_invalid_fields(self):
        for key in example():
            for value in (None,'invalid'):
                with self.subTest(key=key,value=value):
                    f=example()
                    if value is None:del f[key]
                    else:f[key]=value
                    with self.assertRaises(ValueError):b.validate_report(raw(f),'default',0)

    def test_bad_numbers_and_completion(self):
        for key,value in [('c0.elapsed_ms','50000'),('c1.samples','0'),('c0.samples','999'),
                          ('c0.min_ws','2200000'),('c0.peak_commit','1'),
                          ('c0.last_faults','1'),('c0.available_after','999999999'),
                          ('c1.start_tick','0'),('c0.wait','258'),('c2.exit','1'),
                          ('c0.ended.high','9'),('c0.user.high','2'),
                          ('c0.pid','-1'),('c0.pid','4294967296'),('c0.pid','0001'),
                          ('c1.physical_total','67108863'),('completed','2')]:
            f=example();f[key]=value
            with self.subTest(key=key,value=value):
                with self.assertRaises(ValueError):b.validate_report(raw(f),'default',0)

    def test_extra_duplicate_race_and_backend(self):
        f=example();f['c0.exit_sample_race']='1'
        self.assertTrue(b.validate_report(raw(f),'default',0)['passed'])
        for bad in [raw(example())+b'completed=3\r\n',raw(example())+b'ignored=1\r\n']:
            with self.assertRaises(ValueError):b.validate_report(bad,'default',0)
        with self.assertRaises(ValueError):b.validate_report(raw(example()),'hel',0)
        with self.assertRaises(ValueError):b.validate_report(raw(example()),'default',98)


if __name__=='__main__':unittest.main()
