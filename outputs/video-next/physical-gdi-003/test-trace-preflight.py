"""Offline regression for the stale diagnostic trace that blocked physical002."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('trial',k/'trial.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class FakeFTP:
    def __init__(self,data,corrupt=False):
        self.data=data;self.corrupt=corrupt;self.writes=0
    def retrbinary(self,command,receive,blocksize):
        assert command=='RETR '+m.trace
        receive(self.data)
    def storbinary(self,command,stream,blocksize):
        assert command=='STOR '+m.trace
        self.writes+=1;self.data=stream.read()
        if self.corrupt:self.data=self.data[:16]+b'X'+self.data[17:]

class TracePreflight(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        m.art=Path(self.temp.name);m.record=m.art/'trial.json'
        m.r={'preserved':{}}
    def tearDown(self):self.temp.cleanup()
    def test_used_trace_preserved_then_seeded(self):
        old=m.trace_seed[:16]+(41).to_bytes(4,'little')+m.trace_seed[20:]
        f=FakeFTP(old);m.reseed_trace(f)
        self.assertEqual((m.art/'before-video-trace.bin').read_bytes(),old)
        self.assertEqual(f.data,m.trace_seed)
        self.assertTrue(json.loads(m.record.read_text())['trace_reseed_verified'])
    def test_seed_accepted(self):
        f=FakeFTP(m.trace_seed);m.reseed_trace(f)
        self.assertEqual(f.data,m.trace_seed)
    def test_unknown_trace_preserved_but_never_overwritten(self):
        for old in [b'BAD!'+m.trace_seed[4:],m.trace_seed[:2048]]:
            with self.subTest(size=len(old)):
                evidence=m.art/'before-video-trace.bin'
                if evidence.exists():evidence.unlink()
                f=FakeFTP(old)
                with self.assertRaises(AssertionError):m.reseed_trace(f)
                self.assertEqual(evidence.read_bytes(),old)
                self.assertEqual(f.writes,0)
    def test_bad_readback_blocks_verification(self):
        f=FakeFTP(m.trace_seed,corrupt=True)
        with self.assertRaises(AssertionError):m.reseed_trace(f)
        self.assertNotIn('trace_reseed_verified',json.loads(m.record.read_text()))

if __name__=='__main__':unittest.main()
