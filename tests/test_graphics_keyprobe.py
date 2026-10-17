# SPDX-License-Identifier: MIT
import sys
from pathlib import Path
import struct
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_keyprobe as g


class KeyProbeTests(unittest.TestCase):
    def test_geometry_and_key_distinction(self):
        self.assertEqual(len(g.SOURCE),192)
        self.assertEqual(g.SOURCE[:8],(0,0xff0000,0x010000,1,0xff00,0x123456,0xab3456,0x123457))
        plain=g.expected(0);zero=g.expected(1);red=g.expected(5);other=g.expected(9)
        self.assertEqual(plain[4*32+4],0)
        self.assertEqual(zero[4*32+4],0x335577)
        self.assertEqual(zero[4*32+5],0xff0000)
        self.assertEqual(red[4*32+4],0)
        self.assertEqual(red[4*32+5],0x335577)
        self.assertEqual(other[4*32+9],0x335577)
        self.assertEqual(other[4*32+10],0xab3456)
        for stage in range(12):
            result=g.expected(stage)
            self.assertEqual(len(result),768)
            for y in range(24):
                for x in range(32):
                    outside=x<4 or x>=20 or y<4 or y>=16
                    if (stage//2)%2:outside=outside or y<5 or y>=15 or not(6<=x<12 or 14<=x<19)
                    if outside:self.assertEqual(result[y*32+x],0x335577)
        self.assertNotEqual(g.expected(1),g.expected(5))
        for stage in (-1,12,True,'0'):
            with self.assertRaises(ValueError):g.expected(stage)

    def test_synthetic_transport_and_failures(self):
        f={'schema':'xwn-keyprobe-1','backend':'default','scope':'owned-rgb32-system-memory',
           'os.major':5,'os.minor':0,'os.build':2195,'modes.complete':1,'modes.count':1,
           'window.create':1,'ddraw.load':1,'ddraw.entry':1,'clipper.exact':1,
           'cleanup.clipper.attached':1,'ddraw.unload':1,'completed':12,'end':'complete',
           'mismatches':0,'exit':0,'result':'KEYPROBE_OK'}
        for prefix in ('mode','desktop','m0'):
            f.update({prefix+'.width':640,prefix+'.height':480,prefix+'.bpp':16})
        f.update({'m0.hz':60,'m0.flags':0})
        for k in ('ddraw.create','ddraw.cooperative','ddraw.mode','source.create','dest.create','clipper.create','clipper.set','clipper.get','cleanup.clipper'):f[k]='00000000'
        for k in ('dest','source','clipper','ddraw'):f['release.'+k]=0
        for stage in range(12):
            p=f's{stage}.'
            f.update({p+k:v for k,v in [('key.requested',g.KEYS[stage//4]),('key.low',g.KEYS[stage//4]),('key.high',g.KEYS[stage//4]),('keyed',stage%2),('clipped',(stage//2)%2),('complete',1),('source.read.mismatches',0),('dest.read.mismatches',0)]})
            for k in ('key.set','key.get','blit'):f[p+k]='00000000'
            if stage in (2,4,6,8,10):f[p+'clipper.change']='00000000'
            for label in ['dest.write','source.read','dest.read']+(['source.write'] if stage==0 else []):
                f.update({p+label+'.lock':'00000000',p+label+'.unlock':'00000000',p+label+'.layout':1,p+label+'.pitch':64 if label.startswith('source') else 128})
        encode=lambda data:''.join(f'{k}={v}\r\n' for k,v in data.items()).encode()
        raw=encode(f);src=struct.pack('<2304I',*(g.SOURCE*12));dst=struct.pack('<9216I',*(v for s in range(12) for v in g.expected(s)))
        self.assertTrue(g.validate(raw,src,dst,'default',0)['semantics_passed'])
        for key in f:
            changed=dict(f);del changed[key]
            with self.assertRaises((ValueError,KeyError)):g.validate(encode(changed),src,dst,'default',0)
        for bad in (raw+b'bad=1\n',raw+b'completed=12\n',raw[:-1]+b'\xff'):
            with self.assertRaises(ValueError):g.validate(bad,src,dst,'default',0)
        for offset in range(0,len(dst),4):
            changed=bytearray(dst);changed[offset]^=1
            with self.assertRaises(ValueError):g.validate(raw,src,changed,'default',0)
        for data in (src[:-1],src+b'\0'):
            with self.assertRaises(ValueError):g.validate(raw,data,dst,'default',0)
        # Faithfully reported mismatch is a complete diagnostic FAILURE, never PASS.
        changed=bytearray(dst);changed[0]^=1
        failure=dict(f,mismatches=1,exit=1,result='FAILED');failure['s0.dest.read.mismatches']=1
        result=g.validate(encode(failure),src,changed,'default',1)
        self.assertTrue(result['complete_observation']);self.assertFalse(result['semantics_passed'])
        with self.assertRaises(ValueError):g.validate(encode(failure),src,changed,'default',0)


if __name__=='__main__':unittest.main()
