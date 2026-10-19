# SPDX-License-Identifier: MIT
"""Independent malformed-counter controls, plus inherited pixel endpoints."""
import unittest
import hashlib
import test_graphics_scenepresent as base
import graphics_sceneloop as g


def fixture():
    f,data=base.fixture()
    f.update(schema='xwn-scene-loop-2',scope='repeated-windowed-xyz-software-phase-costs')
    f.pop('end')
    def put(k,v): f['loop.'+k]=v
    def wide(k,v): put(k+'.low',v&0xffffffff);put(k+'.high',v>>32)
    for k in ('psapi.load','psapi.entry','psapi.unload'):put(k,1)
    put('frames_per_stage',512);put('batch_deadline_ms',30000);wide('frequency',1000000)
    for i,elapsed in enumerate((250,1000)):
        p=f'cal{i}.';put(p+'request_ms',elapsed);put(p+'elapsed_ms',elapsed)
        wide(p+'start',i*1000000);wide(p+'end',i*1000000+elapsed*1000)
    for stem in ['before']+[f's{i}.{w}' for i in range(5) for w in ('before','after')]+['released']:
        for n,v in dict(ws=2**20,peak_ws=2**21,commit=2**19,peak_commit=2**20,faults=42).items():put(f'mem.{stem}.{n}',v)
    for i in range(5):
        p=f's{i}.';put(p+'frames',512);put(p+'elapsed_ms',100)
        wide(p+'start',2**32+i*200000);wide(p+'end',2**32+i*200000+100000)
        for n,v in dict(render=50000,upload=20000,present=10000).items():wide(p+n,v);put(p+n+'_tick_ms',v//1000)
    n=int(f['modules']);f['module'+str(n)+'.path']='C:\\WINNT\\system32\\psapi.dll'.encode().hex();f['module'+str(n)+'.bytes']=16384;f['modules']=n+1
    f['end']='complete'
    return {k:str(v) for k,v in f.items()},data


class LoopTests(unittest.TestCase):
    def test_valid_and_wrap(self):
        f,data=fixture();r=g.validate(base.base.encode(f),*data,'default',0)
        self.assertEqual(r['sustained_frames'],2560)
        self.assertEqual(r['report_sha256'],hashlib.sha256(base.base.encode(f)).hexdigest())
        self.assertEqual(r['telemetry']['rows'][0]['qpc_render_ms'],50)
    def test_every_loop_field_required_and_numeric(self):
        f,_=fixture()
        for k in f:
            if not k.startswith('loop.'):continue
            for remove in (True,False):
                bad=dict(f)
                if remove:del bad[k]
                else:bad[k]='invalid'
                with self.assertRaises(ValueError,msg=k):g.telemetry(bad)
    def test_order_clock_budget_and_unknown(self):
        f,_=fixture()
        for k,v in [('loop.s1.start.high','0'),('loop.s0.end.low','0'),('loop.frequency.low','0'),
                    ('loop.s0.render.low','100001'),('loop.s0.elapsed_ms','1000'),
                    ('loop.s0.frames','31'),('loop.mem.released.ws',str(9*1024**2)),
                    ('loop.s0.start.high',str(2**31)),('loop.extra','1'),('loop.s0.render_tick_ms','101'),('loop.cal1.elapsed_ms','0')]:
            bad=dict(f);bad[k]=v
            with self.assertRaises(ValueError,msg=k):g.telemetry(bad)
    def test_uncalibrated_qpc_not_converted(self):
        f,_=fixture();f['loop.frequency.high']='6';f['loop.frequency.low']='764646224'
        r=g.telemetry(f)
        self.assertFalse(r['qpc_calibrated'])
        self.assertIsNone(r['rows'][0]['qpc_render_ms'])
        self.assertEqual(r['rows'][0]['render_tick_ms'],50)
    def test_endpoint_corruption_and_missing_psapi(self):
        f,data=fixture();bad=list(data);b=bytearray(bad[6]);b[0]^=1;bad[6]=b
        with self.assertRaises(ValueError):g.validate(base.base.encode(f),*bad,'default',0)
        n=int(f['modules'])-1;f.pop('module'+str(n)+'.path');f.pop('module'+str(n)+'.bytes');f['modules']=str(n)
        with self.assertRaises(ValueError):g.validate(base.base.encode(f),*data,'default',0)


if __name__=='__main__':unittest.main()
